from ImageSteganography import ImageSteganography
from PIL import Image
import os

# File paths
host_path = "host.png"           # a large image (e.g. 800x800 or bigger)
secret_path = "secret.png"       # a smaller image (e.g. 100x100)
output_encoded = "encoded_output.png"
output_decoded = "decoded_output.png"

# Initialize with the same num_lsb for both steps
steg = ImageSteganography(num_lsb=2)

# Step 1: Encode
print("🔐 Encoding...")
steg.encode_info(host_path, secret_path, output_encoded)

# Step 2: Decode
print("🔎 Decoding...")
decoded_img = steg.decode_info(output_encoded)

# Step 3: Save decoded image if successful
if decoded_img:
    decoded_img.save(output_decoded)
    print(f"✅ Decoded image saved to {output_decoded}")
else:
    print("❌ Failed to decode hidden image.")
