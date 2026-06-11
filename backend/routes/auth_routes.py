# routes/auth_routes.py
from flask import Blueprint  # type: ignore[import]
from controllers.auth_controller import AuthController

auth_bp = Blueprint('auth', __name__)

auth_bp.route('/register', methods=['POST'])(AuthController.register)
auth_bp.route('/login',    methods=['POST'])(AuthController.login)
auth_bp.route('/profile',  methods=['GET'])(AuthController.get_profile)  # ← new