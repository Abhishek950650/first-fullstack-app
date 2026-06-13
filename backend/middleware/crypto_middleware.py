# middleware/crypto_middleware.py
from flask import request, jsonify, g
from functools import wraps
from utils.encryption import encrypt_data, decrypt_data
from config import ENABLE_ENCRYPTION


def decrypt_request(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method == 'GET':
            return f(*args, **kwargs)

        raw = request.get_json()

        if not raw:
            return jsonify({
                'success': False,
                'message': 'Invalid request'
            }), 400

        if ENABLE_ENCRYPTION:
            # Production → encrypted data expect karo
            if 'data' not in raw:
                return jsonify({
                    'success': False,
                    'message': 'Encrypted data expected'
                }), 400
            try:
                g.decrypted_body = decrypt_data(raw['data'])
                # print(f"[PROD] Decrypted Request: {g.decrypted_body}")
            except Exception:
                return jsonify({
                    'success': False,
                    'message': 'Decryption failed'
                }), 400
        else:
            # Development → plain JSON as-is use karo
            g.decrypted_body = raw
            # print(f"[DEV]  Plain Request: {g.decrypted_body}")

        return f(*args, **kwargs)
    return decorated


def encrypt_response(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        response = f(*args, **kwargs)

        if isinstance(response, tuple):
            resp_data, status_code = response
        else:
            resp_data, status_code = response, 200

        actual_data = resp_data.get_json()

        if ENABLE_ENCRYPTION:
            # Production → encrypt karke bhejo
            encrypted = encrypt_data(actual_data)
            # print(f"[PROD] Encrypted Response: {encrypted[:30]}...")
            return jsonify({'data': encrypted}), status_code
        else:
            # Development → plain JSON bhejo
            # print(f"[DEV]  Plain Response: {actual_data}")
            return jsonify(actual_data), status_code

    return decorated