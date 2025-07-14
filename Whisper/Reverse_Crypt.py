from protection import *

class ReverseCrypt(PasswordProtection):
    def __init__(self):
        super().__init__()

    def Encrypt(self, text: str) -> str:
        try:
            utf8_bytes = text.encode('utf-8')
            reversed_bytes = utf8_bytes[::-1]
            hex_str = reversed_bytes.hex()
            return hex_str
        except Exception as e:
            return f"Error: {e}"

    def Decrypt(self, hex_str: str) -> str:
        try:
            reversed_bytes = bytes.fromhex(hex_str)
            original_bytes = reversed_bytes[::-1]
            return original_bytes.decode('utf-8')
        except Exception as e:
            return f"Error: {e}"

"""
rev = ReverseCrypt()

res = rev.Encrypt("გამარჯობა")

print("🔐 HEX Encrypted:", res)

res1 = rev.Decrypt(res)
print("🔓 Decrypted:", res1)
"""