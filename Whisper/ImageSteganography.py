from PIL import Image
import os
import math  # მათემატიკური ოპერაციებისთვის ზომის შესამცრირებლად და ჰოსტ ტოტოს ზომებზე მოსარგბლად


class ImageSteganography:
    def __init__(self, num_lsb=1):
        if not 1 <= num_lsb <= 8:
            raise ValueError("num_lsb be beteawen  1 and  8")
        self.num_lsb = num_lsb
        self.clear_mask = ~((1 << self.num_lsb) - 1)
        self.extract_mask = (1 << self.num_lsb) - 1

    def _int_to_bits(self, n, num_bits_total=32):
        return format(n, f'0{num_bits_total}b')

    def _bits_to_int(self, bit_string):
        return int(bit_string, 2)

    def _get_image_binary_data(self, image):
        binary_data_list = []
        width, height = image.size
        for y in range(height):
            for x in range(width):
                r, g, b = image.getpixel((x, y))
                binary_data_list.append(self._int_to_bits(r, 8))
                binary_data_list.append(self._int_to_bits(g, 8))
                binary_data_list.append(self._int_to_bits(b, 8))
        return "".join(binary_data_list)

    def encode_info(self, host_path, secret_path, output_path):
        try:
            host_img = Image.open(host_path).convert('RGB')
            secret_img_original = Image.open(secret_path).convert(
                'RGB')  # ვტვირთავთ პოტოს ასლსს შესაძლო ზომის შესაცვლელად
            secret_img = secret_img_original.copy()  # ვმუშაობთ ასლთან
        except FileNotFoundError:
            print(f"Error, one file from there can't be found  ({host_path} or {secret_path})")
            return
        except Exception as e:
            print(f"  {e}")
            return

        c_width, c_height = host_img.size

        # --- ვცვლით ჩასაშენებელი ფოტოს ზომებს თუ იგი არ ეტევა ჰოსტ ფოტოში ---
        capacity = c_width * c_height * 3 * self.num_lsb

        current_s_width, current_s_height = secret_img.size
        required_bits = 64 + current_s_width * current_s_height * 24

        if required_bits > capacity:
            print(
                f"ℹ secret image (bit {required_bits} needen) so large for container (avable {capacity} bit).")

            max_data_bits_for_pixels = capacity - 64
            if max_data_bits_for_pixels < 24:  # minimum for 1 pixel (3 channel * 8 bit)
                print(
                    f" Error: metadata is too small (needen >={64 + 24} bit).")
                return

            target_pixel_area = math.floor(max_data_bits_for_pixels / 24)
            if target_pixel_area <= 0:
                print(f" error coneiner can't add any pixel after metadata.")
                return

            original_aspect_ratio = current_s_width / current_s_height

            s_new_h = math.floor(math.sqrt(target_pixel_area / original_aspect_ratio))
            s_new_h = max(1, s_new_h)
            s_new_w = math.floor(original_aspect_ratio * s_new_h)
            s_new_w = max(1, s_new_w)

            #ინტერვალურად ვამცირებთ ომას თუ იგი ცოტაც მეტია დამრგვალების შემდეგ
            while (s_new_w * s_new_h > target_pixel_area) and (s_new_w > 1 or s_new_h > 1):
                if original_aspect_ratio >= 1:  # Шире или квадрат
                    if s_new_w > 1:
                        s_new_w -= 1
                    elif s_new_h > 1:
                        s_new_h -= 1
                    else:
                        break
                else:  # Выше
                    if s_new_h > 1:
                        s_new_h -= 1
                    elif s_new_w > 1:
                        s_new_w -= 1
                    else:
                        break

            s_new_w = max(1, s_new_w)
            s_new_h = max(1, s_new_h)

            if s_new_w * s_new_h > target_pixel_area or s_new_w == 0 or s_new_h == 0:
                print(
                    f" Error: can't calculate avable size for image ({s_new_w}x{s_new_h}, summar of pixels.: {target_pixel_area})")
                return

            print(
                f"    change size of secret image ({current_s_width}x{current_s_height}) from ({s_new_w}x{s_new_h}).")
            try:
                resample_filter = Image.Resampling.LANCZOS
            except AttributeError:
                if hasattr(Image, 'LANCZOS'):
                    resample_filter = Image.LANCZOS
                else:
                    resample_filter = Image.ANTIALIAS  # for very old version
            secret_img = secret_img.resize((s_new_w, s_new_h), resample_filter)
            current_s_width, current_s_height = secret_img.size  # ზომების განახლება
        # --- ზომისც შემცირების დასრულების ლოგიკა ---

        metadata_bits = self._int_to_bits(current_s_width, 32) + self._int_to_bits(current_s_height, 32)
        secret_pixel_bits = self._get_image_binary_data(secret_img)
        all_secret_bits_str = metadata_bits + secret_pixel_bits
        total_secret_bits_len = len(all_secret_bits_str)

        if total_secret_bits_len > capacity:  # საბოლოო შემოწმება
            print(
                f" CRITICAL ERROR: after changing size can't put in conteiner  ({total_secret_bits_len} bit) size is so large  ({capacity} бит).")
            print(f"     secret image size after resize: {current_s_width}x{current_s_height}")
            return

        encoded_img = host_img.copy()
        encoded_pixels = encoded_img.load()
        data_idx = 0
        for y_c in range(c_height):
            for x_c in range(c_width):
                if data_idx >= total_secret_bits_len: break
                r_orig, g_orig, b_orig = host_img.getpixel((x_c, y_c))
                new_pixel_channels = []
                for original_channel_val in [r_orig, g_orig, b_orig]:
                    if data_idx >= total_secret_bits_len:
                        new_pixel_channels.append(original_channel_val)
                        continue
                    bits_to_take_from_secret = min(self.num_lsb, total_secret_bits_len - data_idx)
                    secret_chunk_str = all_secret_bits_str[data_idx: data_idx + bits_to_take_from_secret]
                    secret_chunk_val = self._bits_to_int(secret_chunk_str)
                    cleared_channel = original_channel_val & self.clear_mask
                    new_channel_val = cleared_channel | secret_chunk_val
                    new_pixel_channels.append(new_channel_val)
                    data_idx += bits_to_take_from_secret
                encoded_pixels[x_c, y_c] = tuple(new_pixel_channels)
            if data_idx >= total_secret_bits_len: break

        try:
            encoded_img.save(output_path)
            print(f"\n✅ Extraction complete in {output_path}")
        except Exception as e:
            print(f" Error saving image: {e}")


    def check_content(self, image_path):
        try:
            img = Image.open(image_path).convert("RGB")
            c_width, c_height = img.size

            bits_str = ""
            for y_c in range(c_height):
                for x_c in range(c_width):
                    r, g, b = img.getpixel((x_c, y_c))
                    for channel_val in [r, g, b]:
                        extracted_lsb_val = channel_val & self.extract_mask
                        bits_str += self._int_to_bits(extracted_lsb_val, self.num_lsb)
                        if len(bits_str) >= 64:
                            break
                    if len(bits_str) >= 64:
                        break
                if len(bits_str) >= 64:
                    break

            s_width = self._bits_to_int(bits_str[0:32])
            s_height = self._bits_to_int(bits_str[32:64])

            check_size = lambda s_width,s_height : 0 < s_width < 20000 and 0 < s_height < 20000
            return check_size(s_width,s_height)

        except Exception as e:
            return f"❌ Error in check_content: {e}"

    def decode_info(self, image_path):
        try:
            encoded_img = Image.open(image_path).convert('RGB')
        except FileNotFoundError:
            print(f" Error: File not found ({image_path})")
            return None
        except Exception as e:
            print(f" Error opening encoded image:: {e}")
            return None

        c_width, c_height = encoded_img.size
        extracted_bits_list = []
        max_possible_bits_payload = c_width * c_height * 3 * self.num_lsb

        # ჩვენ ვაგროვებთ საყოფაცხოვრებო ნივთებს LSB-დან
        # ოპტიმიზაცია: შეგიძლიათ შეაჩეროთ მეტამონაცემების_len_bits + s_width*s_height*24
        # მაგრამ სიმარტივისთვის ჯერ ყველაფერი შევაგროვოთ და მერე გავარკვიოთ.
        # თუმცა, ძალიან დიდი ფაილებისთვის ეს შეიძლება იყოს არაეფექტური მეხსიერების გამოყენების თვალსაზრისით.
        # ჩვენ ახლა ვზღუდავთ ბიტების კოლექციას ისე, რომ არ შეაგროვოს მეტი, თუ მეტამონაცემები უკვე არსებობს.

        bits_str_buffer = ""
        metadata_len_bits = 64
        s_width, s_height = -1, -1
        total_bits_to_extract_once_metadata_known = -1

        for y_c in range(c_height):
            for x_c in range(c_width):
                r, g, b = encoded_img.getpixel((x_c, y_c))
                for channel_val in [r, g, b]:
                    extracted_lsb_val = channel_val & self.extract_mask
                    bits_str_buffer += self._int_to_bits(extracted_lsb_val, self.num_lsb)

                    if s_width == -1 and len(bits_str_buffer) >= metadata_len_bits:
                        try:
                            s_width = self._bits_to_int(bits_str_buffer[0:32])
                            s_height = self._bits_to_int(bits_str_buffer[32:metadata_len_bits])
                            if not (
                                    0 < s_width < 20000 and 0 < s_height < 20000 and s_width * s_height > 0):
                                print(f" Error: size was found ({s_width}x{s_height}) incorrect.")
                                return None
                            print(f"ℹ️ metadata was extracted : width = {s_width}, height = {s_height}")
                            total_bits_to_extract_once_metadata_known = metadata_len_bits + (s_width * s_height * 24)
                        except ValueError:
                            print("  (width/height).")
                            return None

                    if total_bits_to_extract_once_metadata_known != -1 and len(
                            bits_str_buffer) >= total_bits_to_extract_once_metadata_known:
                        break  # ყველა საჭირო ბიტი შეგროვებულია
                if total_bits_to_extract_once_metadata_known != -1 and len(
                        bits_str_buffer) >= total_bits_to_extract_once_metadata_known:
                    break
            if total_bits_to_extract_once_metadata_known != -1 and len(
                    bits_str_buffer) >= total_bits_to_extract_once_metadata_known:
                break

        if s_width == -1:
            print(" Error. not enught dataas fro metada taoutput")
            return None

        if len(bits_str_buffer) < total_bits_to_extract_once_metadata_known:
            print(f" Error: Not enough bits extracted to reconstruct image.")
            print(
                f"   needed {total_bits_to_extract_once_metadata_known} bit, outputed  {len(bits_str_buffer)} bit.")
            return None

        # დაგვყავს საჭირო ზომამდე თუ გამოსატანი ფაილი დიდია
        extracted_bits_str = bits_str_buffer[:total_bits_to_extract_once_metadata_known]

        required_pixel_data_bits = s_width * s_height * 24
        start_pixel_data_idx = metadata_len_bits
        # end_pixel_data_idx = start_pixel_data_idx + required_pixel_data_bits # Уже учтено в total_bits_to_extract_once_metadata_known

        secret_pixel_stream_str = extracted_bits_str[start_pixel_data_idx:]

        try:
            decoded_img = Image.new("RGB", (s_width, s_height))
            decoded_pixels = decoded_img.load()
        except (MemoryError, ValueError) as e:
            print(f" Error creating new image ({s_width}x{s_height}): {e}")
            return None

        current_bit_idx = 0
        for y_s in range(s_height):
            for x_s in range(s_width):
                if current_bit_idx + 24 > len(secret_pixel_stream_str):
                    print("Warning: Data ran out early while restoring pixels.")
                    return decoded_img
                try:
                    r_bits = secret_pixel_stream_str[current_bit_idx: current_bit_idx + 8]
                    g_bits = secret_pixel_stream_str[current_bit_idx + 8: current_bit_idx + 16]
                    b_bits = secret_pixel_stream_str[current_bit_idx + 16: current_bit_idx + 24]
                    decoded_pixels[x_s, y_s] = (
                    self._bits_to_int(r_bits), self._bits_to_int(g_bits), self._bits_to_int(b_bits))
                except (ValueError, IndexError) as e:
                    print(
                        f"Pixel bit decoding/indexing error in ({x_s},{y_s}): {e}. instaled в (0,0,0).")
                    decoded_pixels[x_s, y_s] = (0, 0, 0)
                current_bit_idx += 24

        print(" Extraction complete.")
        return decoded_img







