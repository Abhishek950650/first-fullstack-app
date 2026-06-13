# utils/encryption.py
import json
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from config import AES_SECRET_KEY


# Key exactly 32 bytes honi chahiye (AES-256)
SECRET_KEY = AES_SECRET_KEY.encode('utf-8')[:32]

# IV — Initialization Vector — exactly 16 bytes
IV = b'abhishek-iv-0707'   # exactly 16 chars


def encrypt_payload(data: dict) -> str:
    """
    Dict → JSON string → AES encrypt → base64 string
    """
    try:
        # 1. Dict ko JSON string mein convert karo
        json_data = json.dumps(data)

        # 2. AES cipher banao (CBC mode)
        cipher = AES.new(SECRET_KEY, AES.MODE_CBC, IV)

        # 3. Encrypt karo (padding add karna padta hai)
        encrypted = cipher.encrypt(
            pad(json_data.encode('utf-8'), AES.block_size)
        )

        # 4. Base64 encode karo (string format mein bhejne ke liye)
        return base64.b64encode(encrypted).decode('utf-8')

    except Exception as e:
        raise Exception(f'Encryption failed: {str(e)}')


def decrypt_payload(encrypted_data: str) -> dict:
    """
    Base64 string → AES decrypt → JSON string → Dict
    """
    try:
        # 1. Base64 decode karo
        encrypted_bytes = base64.b64decode(encrypted_data)

        # 2. AES cipher banao (same key aur IV)
        cipher = AES.new(SECRET_KEY, AES.MODE_CBC, IV)

        # 3. Decrypt karo aur padding hata do
        decrypted = unpad(
            cipher.decrypt(encrypted_bytes), AES.block_size
        )

        # 4. JSON string → Dict
        return json.loads(decrypted.decode('utf-8'))

    except Exception as e:
        raise Exception(f'Decryption failed: {str(e)}')