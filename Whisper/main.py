from steganography import  *
from ImageSteganography import *
from  AudioTextSteganography import *
import os
import sys
#მენიუ  უფრო მარტივად აღსაქმელი გახდეს დავწერე ფუნქციები და ვიძახებ Main()-ში
def handle_text_steganography():
    stego = TextSteganography()
    
    while True:
        print("\n📘 Text Steganography:")
        print("1 - Encode message into image")
        print("2 - Decode message from image")
        print("3 - Check file content")
        print("0 - 🔙 Back to Main Menu")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            message = input("\n📝 Enter the message to hide: ")
            input_image = input("📷 Enter input image path: ")
            output_image = input("💾 Enter output image path (.png): ")

            result = stego.encode_info(input_image, message, output_image)
            print(result)

        elif choice == "2":
            image_path = input("\n📷 Enter image with hidden message: ").strip()
            decoded_msg = stego.decode_info(image_path)
            print(f"\n📤 Decoded message: {decoded_msg}")

            save = input("\n💾 Save message to file? (yes/no): ").strip().lower()
            if save == "yes":
                filename = input("Enter filename and path :>> ")

                with open(filename, "w") as f:
                    f.write(decoded_msg)
                print("\n✅ Saved to content.txt")
            else:
                print('\nincorrect input')
        elif choice == "3":
            img_path = input("\n📂 Enter image path (.png only): ").strip()
            has_content = stego.Cheak_Content(img_path)
            result = (f"content was found in {img_path}") if has_content else (f"content was not found in {img_path}")
            print(result)

        elif choice == "0":
            return

        else:
            print("\n❌ Invalid option. Try again.")


def handle_image_steganography():
    while True:
        print("\n🖼️ Image Steganography:")
        print("1 - Encode one image into another")
        print("2 - Decode hidden image")
        print("3)- Check image content")
        print("0 - 🔙 Back to Main Menu")

        choice = input("Choose option: >> ").strip()

        if choice == "1":
            cover_file = input("\n📂 Enter cover image path: ").strip()
            secret_file = input("🕵️ Enter secret image path: ").strip()
            output_file = input("💾 Enter output image path: ").strip()

            if not os.path.exists(cover_file):
                print(f"\n❌ File not found: {cover_file}")
                continue

            if not os.path.exists(secret_file):
                print(f"\n❌ File not found: {secret_file}")
                continue

            steg = ImageSteganography(num_lsb=2)
            steg.encode_info(cover_file, secret_file, output_file)
            print(f"✅ Encoded image saved to: {output_file}")

        elif choice == "2":
            input_file = input("\n📂 Enter image with hidden image: ").strip()
            output_file = input("💾 Enter output path to save decoded image: ").strip()

            steg = ImageSteganography(num_lsb=2)
            decoded_img = steg.decode_info(input_file)

            if decoded_img:
                try:
                    decoded_img.save(output_file)
                    print(f"\n✅ Decoded image saved to: {output_file}")
                except Exception as e:
                    print(f"\n❌ Error saving image: {e}")
            else:
                print("\n❌ Decoding failed.")

        if choice == '3':

            steganographer = ImageSteganography(num_lsb=2)
            check_path = input("📂 Enter image path to check (.png): ").strip()

            if not os.path.exists(check_path):
                print("❌ File not found.")
                continue

            has_content = steganographer.check_content(check_path)

            if has_content is True:
                print(f"✅ Hidden content found in {check_path}")
            elif has_content is False:
                print(f"❌ No hidden content in {check_path}")
            else:
                print(has_content)

        elif choice == "0":
            break



def handle_AudioTextSeteganography():
  while True:
    st = AudioTextSteganography()

    print("\n========AudioText Steganography===============")
    print("1 - Encode one Text in audio")
    print("2 - Decode hidden message from audio")
    print("3)- Check image content")
    print("0 - 🔙 Back to Main Menu")


    make_choice = input("\nChoose operation")


    if make_choice == "1":

        secret_msg = input("\nEnter secret message ::>>")
        audioFile = input("enter audio file namee or path :>>")
        outAudioFile = input("input output path and name:>>")

        res = st.encode_info(secret_msg,audioFile,outAudioFile)
        print (res)

    elif make_choice == '2':
        outAudioFile = input("\nEnter file name with do you want to decode:>>")
        result = st.decode_info(outAudioFile)
        print( f"decoded info : {result}" )

        ch_it = input("\ndo you want to save result in any txt file?>>:")
        if ch_it == "yes":
           with open("\nsecret.txt,'w") as f:
               f.write(result)

    elif make_choice == "3":
       audioFile = input("\nEnter audio file :>>")
       st.Check_Content(audioFile)

    elif make_choice == '0':
         break


def main():
    while True:
        print("\n📂 MAIN MENU")
        print("1 - Text Steganography")
        print("2 - Image Steganography")
        print("3 - TextAudio Steganography ")
        print("0 - ❌ Exit")

        choice = input("\nChoose option: >> ").strip()

        if choice == "0":
            print("\n👋 Exiting program. Goodbye.")
            break

        elif choice == "1":
            handle_text_steganography()

        elif choice == "2":
            handle_image_steganography()

        elif choice == "3":
            handle_AudioTextSeteganography()
        else:
          print("\n❌ Invalid option. Try again.")


if __name__ == "__main__":
    main()




