import os
import base64 
import hashlib
from AESCipher import AESCipher
from Reverse_Crypt import ReverseCrypt
from Cryptography import CaserCipher
from protection import PasswordProtection
from ImageSteganography import ImageSteganography
from AudioTextSteganography import AudioTextSteganography
from steganography import TextSteganography
 
class StegoTextPass:
    def __init__(self):
        self.prot = PasswordProtection()
        self.aes = AESCipher()
        self.reverse = ReverseCrypt()
        self.caser = CaserCipher()
        self.text_steg = TextSteganography()
        self.image_steg = ImageSteganography()
        self.audio_steg = AudioTextSteganography()

        self.ui_algo_map = {
            "Weak": "caser",
            "Medium": "reverse",
            "Strong": "aes"
        }

    def _encrypt(self, algo: str, text: str, password: str) -> str: # ADD 'password: str'
        if algo == "aes":
            self.aes._derive_key(password) # CORRECTED: Use password for key derivation
            encrypted_bytes = self.aes.encrypt(text)
            if not isinstance(encrypted_bytes, bytes):
                raise ValueError("Encryption failed.")
            return base64.b64encode(encrypted_bytes).decode("utf-8")
        elif algo == "reverse":
            return self.reverse.Encrypt(text)
        elif algo == "caser":
            return self.caser.Encrypt(text, shift=self.prot.shift)
        else:
            raise ValueError("Unsupported encryption algorithm")
        
    

    def _decrypt(self, algo: str, encrypted_text: str, password: str) -> str:
        if algo == "aes":
            self.aes._derive_key(password)
            try:
                # Clean and decode Base64
                valid_b64_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
                clean_base64 = ''.join(c for c in encrypted_text if c in valid_b64_chars)
                encrypted_bytes = base64.b64decode(clean_base64, validate=True)
            except Exception as e:
                print("[🧪] Clean Base64 length:", len(clean_base64))

                print("[❌] Base64 decode failed.")
                print("Encrypted text that failed base64 decode:", encrypted_text[:80])  # truncated for debug
                raise ValueError(f"Base64 decode failed: {e}")

            # Now do AES decryption
            if len(encrypted_bytes) < 16:
                raise ValueError("Decryption error: Encrypted data is too short to contain IV.")
            try:
                decrypted = self.aes.decrypt(encrypted_bytes)
                return decrypted
            except Exception as e:
                raise ValueError(f"Decryption error: {e}")

        elif algo == "reverse":
            return self.reverse.Decrypt(encrypted_text)
        elif algo == "caser":
            return self.caser.Decrypt(encrypted_text, shift=self.prot.shift)
        else:
            raise ValueError("Unsupported decryption algorithm")


    def _extract_algo_marker(self, data: bytes):
        """
        Extracts the algorithm marker from the data.
        Assumes data format: [core_data][--PASS--][encrypted_password][--ALGO--][algorithm_label]
        Returns core_pass_split (bytes before --ALGO-- including password part) and algo_encoded (bytes after --ALGO--).
        """
        if b"\n--ALGO--\n" not in data:
            raise ValueError("Algorithm marker '--ALGO--' not found in the file.")
        
        core_pass_split, algo_encoded = data.rsplit(b"\n--ALGO--\n", 1)
        return core_pass_split, algo_encoded

    def encode_text_with_password(self, file_path: str, message: str, password: str, algo_label: str, output_path: str):
        try:
            import hashlib
            algo = self.ui_algo_map.get(algo_label, "aes")
            password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

            # Encrypt the message using the chosen algorithm and password
            encrypted_message = self._encrypt(algo, message, password) # Pass 'password' here

            # Encode content (use the encrypted_message)
            if file_path.endswith(".txt") or file_path.endswith(".png"):
                self.text_steg.encode_info(file_path, encrypted_message, output_path) # Use encrypted_message
            elif file_path.endswith(".mp3"):
                self.audio_steg.encode_info(
                    secret_message=encrypted_message,
                    input_audio_file=file_path,
                    output_audio_file=output_path
                )

            else:
                raise ValueError("Unsupported file type for embedding text.")

            # Append hash + algorithm
            with open(output_path, "ab") as f:
                f.write(b"\n--PASS--\n")
                f.write(password_hash.encode("ascii"))
                f.write(b"\n--ALGO--\n")
                f.write(algo.encode("utf-8"))

            print(f"[✅] Text embedded with password successfully to {output_path}")
        except Exception as e:
            print(f"[❌] Error during text embedding: {e}")



    def encode_image_with_password(self, cover_image_path: str, secret_image_path: str, password: str, algo_label: str, output_path: str):
        try:
            algo = self.ui_algo_map.get(algo_label, "aes")
            password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

            self.image_steg.encode_info(cover_image_path, secret_image_path, output_path)
            with open(output_path, "ab") as f:
                f.write(b"\n--PASS--\n")
                f.write(password_hash.encode("ascii")) # Changed to encode("ascii")
                f.write(b"\n--ALGO--\n")
                f.write(algo.encode("utf-8"))
            print(f"[✅] Image embedded with password successfully to {output_path}")
        except Exception as e:
            print(f"[❌] Error during image embedding: {e}")



    def _extract_password_and_algo(self, data: bytes):
        """
        Extracts core data, encrypted password, and algorithm from the file data.
        Assumes data format: [core_data][--PASS--][encrypted_password][--ALGO--][algorithm_label]
        """
        try:
            # Split into core data and the rest (password + algo)
            parts = data.split(b"\n--PASS--\n")
            if len(parts) < 2:
                raise ValueError("Password marker '--PASS--' not found in the file.")
            
            core_data_before_pass = parts[0]
            rest = parts[1]

            # Split the 'rest' into encrypted password and algorithm
            pass_algo_parts = rest.split(b"\n--ALGO--\n")
            if len(pass_algo_parts) < 2:
                raise ValueError("Algorithm marker '--ALGO--' not found after password marker.")
            
            # Extract raw bytes for password and algorithm
            encrypted_password_raw = pass_algo_parts[0].strip()
            algo_encoded_raw = pass_algo_parts[1].strip() # Use a distinct variable name

            # 1. Decode encrypted_password_raw to a string and clean it
            # Base64 strings are ASCII compatible. Filter out any non-Base64 characters.
            valid_b64_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
            encrypted_password_string = "".join(c for c in encrypted_password_raw.decode("ascii") if c in valid_b64_chars)

            # 2. Decode algo_encoded_raw to a string
            algo_label = algo_encoded_raw.decode("utf-8") # Algorithm label was encoded with utf-8

            # Verify the encrypted password is valid base64 after cleaning
            try:
                base64.b64decode(encrypted_password_string)
            except Exception as e: # Catch specific exception for better error handling
                raise ValueError(f"Encrypted password is not valid base64 data: {e}")

            return core_data_before_pass, encrypted_password_string, algo_label # Return the cleaned strings
        except Exception as e:
            raise ValueError(f"Error parsing file data: {str(e)}")
        

    def encode_audio_with_password(
        self,
        file_path: str,      # original (cover) audio – .mp3, .wav …
        message: str,        # text you want to hide
        password: str,       # password the user supplies
        algo_label: str,     # "Weak" | "Medium" | "Strong"  (stored only for UI)
        output_path: str     # where to save the stego‑audio
    ):
        """
        Convenience wrapper so GUI / scripts can call a dedicated
        'audio' method. Internally re‑uses encode_text_with_password,
        which already handles .mp3 in its switch‑case.
        """
        return self.encode_text_with_password(
            file_path, message, password, algo_label, output_path
        )


    def decode_with_password(self, file_path: str, password: str, data_type: str) -> str | None:


        print("[🛠] File path being decoded:", file_path)
        print("[🛠] Data type passed:", data_type)


        try:
            # Read the entire file content
            with open(file_path, "rb") as f:
                full_content = f.read()

            # Separate core content from password hash and algorithm label
            core_content_with_password_hash, algo_encoded = self._extract_algo_marker(full_content)
            core_content, password_hash_encoded = core_content_with_password_hash.rsplit(b"\n--PASS--\n", 1)
            password_hash = password_hash_encoded.decode("ascii")
            algo = algo_encoded.decode("utf-8")

            # Validate password
            if hashlib.sha256(password.encode('utf-8')).hexdigest() != password_hash:
                raise ValueError("Invalid password.")

            decoded_stego_content = None # Initialize variable

            # Decode based on data_type
            if data_type == "text":
                decoded_stego_content = self.text_steg.decode_info(file_path)
            elif data_type == "image":
                # For image in image, the hidden content itself is usually not encrypted.
                # The 'password protection' is for accessing the stego file and then extracting.
                decoded_stego_content = self.image_steg.decode_info(file_path)
                print(f"[✅] Image content extracted successfully! Output path: {decoded_stego_content}")
                return decoded_stego_content # RETURN DIRECTLY FOR IMAGE TYPE
            elif data_type == "audio":
                decoded_stego_content = self.audio_steg.decode_info(file_path)
            else:
                raise ValueError("Unsupported data type for decoding.")
            
            if decoded_stego_content is None:
                raise ValueError("Could not extract steganographic content.")

            # Decrypt the extracted content only if it's text (hidden in text, image, or audio)
            # For image-in-image, we've already returned above.
            print("[🧪] Extracted stego content (truncated):", decoded_stego_content[:100])

            decrypted_message = self._decrypt(algo, decoded_stego_content, password)
            print(f"[✅] Content decoded and decrypted successfully!")
            return decrypted_message

        except ValueError as ve:
            print(f"[❌] Decoding Failed: {ve}")
            return None
        except FileNotFoundError:
            print(f"[❌] Decoding Failed: File not found at {file_path}")
            return None
        except Exception as e:
            print(f"[❌] An unexpected error occurred during decoding: {e}")
            traceback.print_exc()
            return None

        


    


 
from StegoTextPass import StegoTextPass
import os
 
def main():
    steg = StegoTextPass()
    password = "testpass"
    algo_label = "Weak"
 
    base_folder = "img"
    test_image_path = os.path.join(base_folder, "image.png")
    test_secret_image_path = os.path.join(base_folder, "secret.png")
    test_audio_path = os.path.join(base_folder, "turbo.mp3")
 
    output_text_in_image = os.path.join(base_folder, "out_text_in_image.png")
    output_image_in_image = os.path.join(base_folder, "out_image_in_image.png")
    output_text_in_audio = os.path.join(base_folder, "out_text_in_audio.mp3")
 
    test_message = "Hello, this is a secret message!"
 
    print("=== StegoTextPass Automated Demo ===\n")
 
    print("[1] Embedding text into image...")
    steg.encode_text_with_password(test_image_path, test_message, password, algo_label, output_text_in_image)
    print(f"Output saved to {output_text_in_image}")
 
    print("[1] Extracting text from image...")
    steg.decode_with_password(output_text_in_image, password, data_type="text")
    print()
 
    print("[2] Embedding image into image...")
    steg.encode_image_with_password(test_image_path, test_secret_image_path, password, algo_label, output_image_in_image)
    print(f"Output saved to {output_image_in_image}")
 
    print("[2] Extracting image from image...")
    steg.decode_with_password(output_image_in_image, password, data_type="image")
    print()
 
    print("[3] Embedding text into audio...")
    steg.encode_audio_with_password(test_audio_path, test_message, password, algo_label, output_text_in_audio)
    print(f"Output saved to {output_text_in_audio}")
 
    print("[3] Extracting text from audio...")
    steg.decode_with_password(output_text_in_audio, password)
    print()
 
    print("=== Demo finished ===")

    
 
if __name__ == "__main__":
    main()