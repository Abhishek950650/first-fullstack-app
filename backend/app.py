# app.py
import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from routes.auth_routes import auth_bp

app = Flask(__name__)
# Angular build folder ka path
ANGULAR_BUILD_PATH = os.path.join(
    os.path.dirname(__file__),
    '..', 'frontend', 'dist', 'frontend', 'browser'
)

app = Flask(__name__, static_folder=ANGULAR_BUILD_PATH)

CORS(app, resources={
    r"/api/*": {
        "origins": "*"   # build mein port 4200 nahi hoga isliye * rakho
    }
})
app.register_blueprint(auth_bp, url_prefix='/api/auth')

# ── Angular files serve karo ─────────────────────────
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_angular(path):

    # Pehle API routes ko handle hone do
    if path.startswith('api/'):
        return {'message': 'API not found'}, 404

    # Static file exist karta hai? (js, css, images)
    static_file = os.path.join(ANGULAR_BUILD_PATH, path)
    if path and os.path.exists(static_file):
        return send_from_directory(ANGULAR_BUILD_PATH, path)

    # Baaki sab ke liye index.html do (Angular routing handle karega)
    return send_from_directory(ANGULAR_BUILD_PATH, 'index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)