# 🔐 Fullstack Authentication App

> A production-ready fullstack authentication system built with **Angular**, **Python Flask**, and **MySQL** — implementing enterprise-level security patterns including AES-256 payload encryption, JWT authentication, and MVC architecture.

---

## 🌐 Live Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     CLIENT (Angular)                     │
│                                                         │
│   Register ──► Login ──► Home (Protected)               │
│                                                         │
│   Interceptor Chain:                                    │
│   [CryptoInterceptor] → [AuthInterceptor]               │
│                       → [ErrorInterceptor]              │
└────────────────────┬────────────────────────────────────┘
                     │  HTTPS + Encrypted Payload
                     │  { "data": "U2FsdGVkX1+..." }
┌────────────────────▼────────────────────────────────────┐
│                  SERVER (Flask REST API)                  │
│                                                         │
│   Middleware:  decrypt_request → encrypt_response        │
│   Pattern:     MVC Architecture                         │
│   Routes → Controllers → Models → MySQL                 │
└─────────────────────────────────────────────────────────┘
```

---

## ✨ Features

### 🔑 Authentication
- User **Registration** with input validation
- User **Login** with JWT token generation
- **Logout** with session cleanup (frontend + database)
- Protected routes using **Angular Auth Guard**

### 🛡️ Security Implementation
- **AES-256-CBC** payload encryption on every API request/response
- **JWT tokens** with encrypted payload (user data not visible in token)
- **bcrypt** password hashing (passwords never stored as plain text)
- **Random IV** (Initialization Vector) per encryption — same data gives different output every time
- **Feature flag** based encryption toggle (OFF in dev, ON in production)
- CORS restricted to allowed origins only

### 🏗️ Architecture & Patterns
- **MVC Pattern** on backend (Models, Controllers, Routes separated)
- **Single Responsibility** interceptors on frontend
- **Global Error Handling** via interceptor (401, 403, 500, network errors)
- **Environment-based configuration** for dev vs production
- Database-level **login status tracking** per user
- **Role-based** user system (`user`, `admin`)

---

## 🧰 Tech Stack

### Frontend
| Technology | Version |
|---|---|
| Angular | 20.2.1 |
| Node.js | 22.18.0 |
| npm | 9.8.0 |
| TypeScript | 5.x |
| crypto-js | 4.x |
| RxJS | 7.x |

### Backend
| Technology | Version |
|---|---|
| Python | 3.12.3 |
| Flask | 3.1.x |
| flask-cors | 5.x |
| PyMySQL | 1.x |
| PyJWT | 2.7.x |
| bcrypt | 4.x |
| pycryptodome | 3.x |

### Database
| Technology | Version |
|---|---|
| MariaDB (via XAMPP) | 10.4.32 |
| phpMyAdmin | 5.2.x |

---

## 📁 Project Structure

```
first-fullstack-app/
│
├── backend/                        # Python Flask REST API
│   ├── app.py                      # Entry point + CORS config
│   ├── config.py                   # DB, JWT, AES config + feature flags
│   ├── db.py                       # Database connection helper
│   │
│   ├── models/
│   │   └── user_model.py           # DB queries (find, create, update)
│   │
│   ├── controllers/
│   │   └── auth_controller.py      # Business logic + token_required decorator
│   │
│   ├── routes/
│   │   └── auth_routes.py          # URL → Controller mapping
│   │
│   ├── middleware/
│   │   └── crypto_middleware.py    # decrypt_request + encrypt_response decorators
│   │
│   └── utils/
│       └── encryption.py           # AES-256-CBC encrypt/decrypt functions
│
└── frontend/                       # Angular SPA
    └── src/app/
        ├── pages/
        │   ├── login/              # Login page component
        │   ├── register/           # Register page component
        │   └── home/               # Protected home page component
        │
        ├── services/
        │   ├── auth.service.ts     # API calls + localStorage management
        │   └── encryption.service.ts # AES encrypt/decrypt (crypto-js)
        │
        ├── interceptors/
        │   ├── crypto.interceptor.ts  # Auto encrypt request / decrypt response
        │   ├── auth.interceptor.ts    # Auto attach JWT token
        │   └── error.interceptor.ts   # Global 401/403/500 handling
        │
        ├── guards/
        │   └── auth.guard.ts          # Protect routes from unauthenticated access
        │
        ├── app.routes.ts              # Route definitions
        └── app.config.ts              # App config + interceptor registration
```

---

## 🗄️ Database Schema

```sql
CREATE TABLE users (
    id                INT AUTO_INCREMENT PRIMARY KEY,
    name              VARCHAR(100)  NOT NULL,
    email             VARCHAR(150)  NOT NULL UNIQUE,
    password          VARCHAR(255)  NOT NULL,          -- bcrypt hashed
    user_login_status BOOLEAN       DEFAULT FALSE,     -- session tracking
    user_role         VARCHAR(50)   DEFAULT 'user',    -- role based access
    created_at        TIMESTAMP     DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔐 Security Deep Dive

### 1. AES-256-CBC Payload Encryption

Every API request and response is encrypted — raw data is never transferred over the network.

```
Request Flow:
─────────────
Angular Form Data
      │
      ▼
CryptoInterceptor → AES-256-CBC Encrypt + Random IV
      │
      ▼
{ "data": "U2FsdGVkX1+xK9mN3z..." }  ← what travels on network
      │
      ▼
Flask crypto_middleware → Decrypt → actual JSON
      │
      ▼
Controller handles plain data normally


Response Flow:
──────────────
Controller returns plain JSON
      │
      ▼
Flask crypto_middleware → AES-256-CBC Encrypt
      │
      ▼
{ "data": "Hy73kPqR9xM2..." }  ← what travels on network
      │
      ▼
CryptoInterceptor → Decrypt → Component gets plain data
```

### 2. JWT with Encrypted Payload

Standard JWT tokens have base64-encoded payloads — anyone can decode them. This project encrypts the payload before putting it in the token.

```
Standard JWT payload (❌ visible to anyone):
{ "user_id": 1, "email": "user@test.com", "role": "admin" }

This project's JWT payload (✅ encrypted):
{ "data": "U2FsdGVkX1+...", "exp": 1234567890 }
```

### 3. Feature Flag — Dev vs Production

```python
# config.py
ENABLE_ENCRYPTION = False   # Development — plain JSON, easy debugging
ENABLE_ENCRYPTION = True    # Production  — fully encrypted
```

```typescript
// environment.ts
enableEncryption: false   // ng serve — plain JSON

// environment.prod.ts
enableEncryption: true    // ng build — encrypted automatically
```

### 4. Random IV per Encryption

```
Same data + Fixed IV   → same ciphertext every time ❌ (pattern detectable)
Same data + Random IV  → different ciphertext every time ✅ (secure)
```

### 5. Interceptor Chain (Angular)

```typescript
withInterceptors([
  cryptoInterceptor,   // 1. Encrypt outgoing / Decrypt incoming
  authInterceptor,     // 2. Attach Bearer token to every request
  errorInterceptor     // 3. Handle 401 (logout) / 403 / 500 globally
])
```

---

## 🚀 Getting Started

### Prerequisites

```bash
node --version    # v18+
python --version  # 3.10+
# MySQL/MariaDB running (XAMPP recommended for Windows)
```

### Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install flask flask-cors PyMySQL PyJWT bcrypt pycryptodome
python app.py                  # runs on http://localhost:5000
```

### Database Setup

Run this in phpMyAdmin → SQL tab:

```sql
CREATE DATABASE auth_app;
USE auth_app;

CREATE TABLE users (
    id                INT AUTO_INCREMENT PRIMARY KEY,
    name              VARCHAR(100)  NOT NULL,
    email             VARCHAR(150)  NOT NULL UNIQUE,
    password          VARCHAR(255)  NOT NULL,
    user_login_status BOOLEAN       DEFAULT FALSE,
    user_role         VARCHAR(50)   DEFAULT 'user',
    created_at        TIMESTAMP     DEFAULT CURRENT_TIMESTAMP
);
```

### Frontend Setup

```bash
cd frontend
npm install
ng serve                       # runs on http://localhost:4200
```

### Environment File

Copy the template and fill in your values:

```bash
cp src/environments/environment.template.ts src/environments/environment.ts
```

```typescript
export const environment = {
  production      : false,
  apiUrl          : '/api/auth',
  aesKey          : 'YOUR_32_CHARACTER_AES_KEY_HERE',
  enableEncryption: false
};
```

### Production Build

```bash
cd frontend
ng build                       # Angular build → dist/
cd ../backend
python app.py                  # Flask serves everything on port 5000
```

Visit `http://localhost:5000` — single server serves both frontend and API!

---

## 📡 API Reference

| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| POST | `/api/auth/register` | ❌ | Register new user |
| POST | `/api/auth/login` | ❌ | Login + get JWT token |
| POST | `/api/auth/logout` | ✅ Bearer Token | Logout + update DB status |
| GET | `/api/auth/profile` | ✅ Bearer Token | Get current user info |

> All request bodies and responses are AES-256 encrypted when `ENABLE_ENCRYPTION=True`

---

## 🧠 Key Concepts Implemented

| Concept | Where |
|---|---|
| MVC Architecture | Flask backend |
| Interceptor Pattern | Angular HTTP layer |
| Decorator Pattern | Flask middleware (`@decrypt_request`, `@encrypt_response`) |
| Guard Pattern | Angular route protection |
| Feature Flags | Environment-based encryption toggle |
| Single Responsibility | One interceptor = one job |
| Separation of Concerns | Routes / Controllers / Models / Utils |

---

## 🙋 Author

**Abhishek**
- Frontend Developer expanding into Fullstack
- Angular · Python · MySQL · Flask

---

> ⭐ If this project helped you understand fullstack security patterns, consider starring the repo!