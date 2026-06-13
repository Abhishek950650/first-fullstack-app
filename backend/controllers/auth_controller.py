# controllers/auth_controller.py
from flask import request, jsonify, g
from models.user_model import UserModel
from utils.encryption import encrypt_data, decrypt_data
from middleware.crypto_middleware import decrypt_request, encrypt_response
import jwt
import datetime
from functools import wraps
from config import JWT_SECRET, JWT_EXPIRY


# ── Token verify decorator ───────────────────────────────
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(' ')[1]

        if not token:
            return jsonify({
                'success': False,
                'message': 'Token missing'
            }), 401

        try:
            decoded        = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            encrypted_data = decoded.get('data')
            if not encrypted_data:
                raise Exception('No payload found')
            current_user   = decrypt_data(encrypted_data)

        except jwt.ExpiredSignatureError:
            return jsonify({
                'success': False,
                'message': 'Token expired'
            }), 401
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Invalid token'
            }), 401

        return f(current_user, *args, **kwargs)
    return decorated


class AuthController:

    @staticmethod
    @decrypt_request       # ← request decrypt karo
    @encrypt_response      # ← response encrypt karo
    def register():
        # g.decrypted_body se data lo (request.get_json() nahi)
        data     = g.decrypted_body
        name     = data.get('name', '').strip()
        email    = data.get('email', '').strip()
        password = data.get('password', '').strip()

        if not name or not email or not password:
            return jsonify({
                'success': False,
                'message': 'All fields are required'
            }), 400

        if len(password) < 6:
            return jsonify({
                'success': False,
                'message': 'Password must be at least 6 characters'
            }), 400

        existing = UserModel.find_by_email(email)
        if existing:
            return jsonify({
                'success': False,
                'message': 'Email already registered'
            }), 409

        UserModel.create_user(name, email, password)
        return jsonify({
            'success': True,
            'message': 'Registration successful!'
        }), 201


    @staticmethod
    @decrypt_request       # ← request decrypt karo
    @encrypt_response      # ← response encrypt karo
    def login():
        data     = g.decrypted_body
        email    = data.get('email', '').strip()
        password = data.get('password', '').strip()

        if not email or not password:
            return jsonify({
                'success': False,
                'message': 'Email and password are required'
            }), 400

        user = UserModel.find_by_email(email)
        if not user or not UserModel.verify_password(password, user['password']):
            return jsonify({
                'success': False,
                'message': 'Invalid email or password'
            }), 401

        UserModel.update_login_status(user['id'], True)

        # JWT payload encrypt karo
        user_payload   = {
            'user_id'  : user['id'],
            'name'     : user['name'],
            'email'    : user['email'],
            'user_role': user['user_role']
        }
        encrypted_data = encrypt_data(user_payload)
        jwt_payload    = {
            'data': encrypted_data,
            'exp' : datetime.datetime.utcnow() +
                    datetime.timedelta(hours=JWT_EXPIRY)
        }
        token = jwt.encode(jwt_payload, JWT_SECRET, algorithm='HS256')

        return jsonify({
            'success': True,
            'message': 'Login successful!',
            'token'  : token,
            'user'   : {
                'id'               : user['id'],
                'name'             : user['name'],
                'email'            : user['email'],
                'user_role'        : user['user_role'],
                'user_login_status': True
            }
        }), 200


    @staticmethod
    @token_required
    @encrypt_response      # ← response encrypt karo
    def logout(current_user):
        UserModel.update_login_status(current_user['user_id'], False)
        return jsonify({
            'success': True,
            'message': 'Logged out successfully!'
        }), 200


    @staticmethod
    @token_required
    @encrypt_response
    def get_profile(current_user):
        return jsonify({
            'success': True,
            'user'   : {
                'id'       : current_user['user_id'],
                'name'     : current_user['name'],
                'email'    : current_user['email'],
                'user_role': current_user['user_role']
            }
        }), 200