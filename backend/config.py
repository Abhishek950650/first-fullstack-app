# config.py
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',        # XAMPP mein default password blank hota hai
    'database': 'first_fullstack_app'
}

JWT_SECRET  = 'abhishek-super-secret-key-2026'  # strong key rakho
JWT_EXPIRY  = 24   # hours mein — token 24 ghante baad expire hoga

# AES key — exactly 32 characters hona chahiye (AES-256)
AES_SECRET_KEY = 'abhishek-aes-key-exactly-32chars'  # ← 32 chars count karo