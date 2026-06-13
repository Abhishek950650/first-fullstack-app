# middleware/crypto_middleware.py
from flask import request, jsonify, g
from functools import wraps
from utils.encryption import encrypt_data, decrypt_data


def decrypt_request(f):
    """
    Request body decrypt karo before controller
    
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # GET requests mein body nahi hota
        if request.method == 'GET':
            return f(*args, **kwargs)

        raw = request.get_json()

        # Encrypted data check karo
        if not raw or 'data' not in raw:
            return jsonify({
                'success': False,
                'message': 'Invalid request format — encrypted data expected'
            }), 400

        try:
            # Decrypt karo aur g object mein store karo
            # g = Flask ka global request context object
            g.decrypted_body = decrypt_data(raw['data'])
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Request decryption failed'
            }), 400

        return f(*args, **kwargs)
    return decorated


def encrypt_response(f):
    """
    Response encrypt karke bhejo
    
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # Controller ka response lo
        response      = f(*args, **kwargs)

        # Flask tuple return karta hai (response_dict, status_code)
        if isinstance(response, tuple):
            resp_data, status_code = response
        else:
            resp_data, status_code = response, 200

        # jsonify object se dict nikalo
        actual_data = resp_data.get_json()

        # Encrypt karo
        encrypted = encrypt_data(actual_data)

        # Encrypted format mein bhejo
        return jsonify({'data': encrypted}), status_code

    return decorated