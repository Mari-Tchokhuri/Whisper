import shutil
import base64
from mutagen.id3 import ID3, COMM, ID3NoHeaderError
# , ID3NoTagsError
from steganography import *

class AudioTextSteganography(Steganography):
    def __init__(self):

        self.secret_message = ''
        self.input_audio_file = ''
        self.output_audio_file = ''

    def encode_info(self, secret_message: str, input_audio_file: str, output_audio_file: str):
        try:
            shutil.copyfile(input_audio_file, output_audio_file)

            # Step 1: Validate it's base64
            try:
                # Clean and re-encode to ensure it's valid base64
                if not isinstance(secret_message, str):
                    raise ValueError("Secret message must be a string.")

                # Remove any whitespace or newline characters
                cleaned = ''.join(secret_message.strip().split())

                # Try decoding to ensure it's valid base64
                decoded = base64.b64decode(cleaned, validate=True)

                # Re-encode to canonical base64 format
                safe_encoded = base64.b64encode(decoded).decode('utf-8')
            except Exception as e:
                print("[❌] Invalid Base64 content:", e)
                return

            # Step 2: Add to ID3 tag
            try:
                tags = ID3(output_audio_file)
            except ID3NoHeaderError:
                print(f"{output_audio_file}: ID3 header not found. Creating new ID3 tag.")
                tags = ID3()

            tags.delall("COMM:hidden_steg_text:eng")
            tags.add(COMM(encoding=3, lang='eng', desc='hidden_steg_text', text=safe_encoded))
            tags.save(output_audio_file, v1=0, v2_version=3)
            print(f"[✅] Message was successfully encoded into '{output_audio_file}'")
        except FileNotFoundError:
            print(f"[❌] Error: input file '{input_audio_file}' was not found.")
        except IOError as e:
            print(f"[❌] I/O error during file operations: {e}")
        except Exception as e:
            print(f"[❌] Unexpected error: {e}")

    def decode_info(self, audio_file_path: str):
        try:
            tags = ID3(audio_file_path)
            comment_frames = tags.getall("COMM:hidden_steg_text:eng")

            if not comment_frames:
                print("[❌] No 'hidden_steg_text' frame found in ID3 tag.")
                return None

            text = comment_frames[0].text
            if not text or not isinstance(text[0], str):
                print("[❌] Empty or invalid text in 'hidden_steg_text'.")
                return None

            raw_message = text[0].strip()
            print(f"[🧪] Raw extracted message (truncated): {raw_message[:60]}")

            # Clean Base64
            valid_b64_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
            clean_base64 = ''.join(c for c in raw_message if c in valid_b64_chars)

            print(f"[🧪] Clean Base64 length: {len(clean_base64)}")
            return clean_base64
        except Exception as e:
            print("[❌] Failed to decode audio file:", e)
            return None



    def Check_Content(self, audio_file_path: str) -> bool:
        try:
            tags = ID3(audio_file_path)
            comment_frames = tags.getall("COMM:hidden_steg_text:eng")
            if comment_frames and comment_frames[0].text:
                print(f"✅ Hidden data found in {audio_file_path}")
                return True
            else:
                print(f"ℹ️ No hidden data found in {audio_file_path}")
                return False
        except (ID3NoHeaderError):
            print(f"ℹ️ No ID3 tag found in {audio_file_path}")
        except FileNotFoundError:
            print(f"❌ File not found: {audio_file_path}")
        except Exception as e:
            print(f"❗ Error checking content: {e}")
        return False
