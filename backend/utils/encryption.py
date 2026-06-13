# utils/encryption.py
import json
import base64
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from config import AES_SECRET_KEY

SECRET_KEY = AES_SECRET_KEY.encode('utf-8')[:32]  # 32 bytes AES-256


def encrypt_data(data: dict) -> str:
    """
    Dict → JSON → AES Encrypt → base64
    Random IV har baar naya generate hoga
    """
    json_str     = json.dumps(data)
    iv           = os.urandom(16)          # random 16 bytes IV
    cipher       = AES.new(SECRET_KEY, AES.MODE_CBC, iv)
    encrypted    = cipher.encrypt(
                       pad(json_str.encode('utf-8'), AES.block_size)
                   )
    # IV + encrypted data saath bhejo — decrypt ke time IV chahiye
    combined     = iv + encrypted
    return base64.b64encode(combined).decode('utf-8')


def decrypt_data(encrypted_str: str) -> dict:
    """
    base64 → IV alag karo → AES Decrypt → JSON → Dict
    """
    combined      = base64.b64decode(encrypted_str)
    iv            = combined[:16]           # pehle 16 bytes = IV
    encrypted     = combined[16:]           # baaki = actual data
    cipher        = AES.new(SECRET_KEY, AES.MODE_CBC, iv)
    decrypted     = unpad(cipher.decrypt(encrypted), AES.block_size)
    return json.loads(decrypted.decode('utf-8'))