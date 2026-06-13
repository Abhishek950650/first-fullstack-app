# controllers/auth_controller.py
from utils.encryption import encrypt_payload, decrypt_payload
from models.user_model import UserModel
from config import JWT_SECRET, JWT_EXPIRY
from functools import wraps
from flask import request, jsonify
import jwt
import datetime

# ── Token verify decorator ──────────────────────────────
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Header se token lo
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            token = auth_header.split(' ')[1]  # "Bearer <token>"

        if not token:
            return jsonify({
                'success': False,
                'message': 'Token missing'
            }), 401

        try:
            # 1. JWT verify karo — signature check
            decoded = jwt.decode(
                token, JWT_SECRET, algorithms=['HS256']
            )

            # 2. Encrypted payload nikalo
            encrypted_data = decoded.get('data')
            if not encrypted_data:
                raise Exception('No payload found')

            # 3. Payload decrypt karo
            current_user = decrypt_payload(encrypted_data)
        except jwt.ExpiredSignatureError:
            return jsonify({
                'success': False,
                'message': 'Token expired — please login again'
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                'success': False,
                'message': 'Invalid token'
            }), 401
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Token invalid: {str(e)}'
            }), 401

        return f(current_user, *args, **kwargs)
    return decorated


class AuthController:

    @staticmethod
    def register():
        data     = request.get_json()
        name     = data.get('name', '').strip()
        email    = data.get('email', '').strip()
        password = data.get('password', '').strip()

        # Validation
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

        # Email already exists?
        existing = UserModel.find_by_email(email)
        if existing:
            return jsonify({
                'success': False,
                'message': 'Email already registered'
            }), 409

        # User banao
        UserModel.create_user(name, email, password)
        return jsonify({
            'success': True,
            'message': 'Registration successful!'
        }), 201

    @staticmethod
    def login():
        data     = request.get_json()
        email    = data.get('email', '').strip()
        password = data.get('password', '').strip()

        # 1. Validation
        if not email or not password:
            return jsonify({
                'success': False,
                'message': 'Email and password are required'
            }), 400

        # 2. User dhundo database mein
        user = UserModel.find_by_email(email)
        if not user:
            return jsonify({
                'success': False,
                'message': 'Invalid email or password'  # intentionally same message
            }), 401

        # 3. Password verify karo
        password_match = UserModel.verify_password(password, user['password'])
        if not password_match:
            return jsonify({
                'success': False,
                'message': 'Invalid email or password'
            }), 401

        # Login status TRUE karo
        UserModel.update_login_status(user['id'], True)

        # 4.1 Sensitive payload banao
        user_payload = {
            'user_id'  : user['id'],
            'name'     : user['name'],
            'email'    : user['email'],
            'user_role': user['user_role']
        }

        # 4.2 Payload AES encrypt karo
        encrypted_data = encrypt_payload(user_payload)

        # 4.3 Encrypted data JWT mein daalo
        jwt_payload = {
            'data': encrypted_data,    # ← actual data encrypted hai
            'exp' : datetime.datetime.utcnow() +
                    datetime.timedelta(hours=JWT_EXPIRY)
        }

        token = jwt.encode(jwt_payload, JWT_SECRET, algorithm='HS256')
        
        # 5. Token return karo
        return jsonify({
            'success' : True,
            'message' : 'Login successful!',
            'token'   : token,
            'user'    : {
                'id'   : user['id'],
                'name' : user['name'],
                'email': user['email'],
                'user_role': user['user_role'],
                'user_login_status': user['user_login_status']
            }
        }), 200
    
    @staticmethod
    @token_required
    def get_profile(current_user):
        return jsonify({
            'success': True,
            'user'   : {
                'id'   : current_user['user_id'],
                'name' : current_user['name'],
                'email': current_user['email'],
                'user_role': current_user['user_role'],
                'user_login_status': current_user['user_login_status']
            }
        }), 200
    
    @staticmethod
    @token_required
    def logout(current_user):
        # ✅ Logout status FALSE karo
        UserModel.update_login_status(current_user['user_id'], False)

        return jsonify({
            'success': True,
            'message': 'Logged out successfully!'
        }), 200