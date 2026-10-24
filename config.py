import os
from datetime import timedelta
from dotenv import load_dotenv

# Load variables from .env if present
load_dotenv()

# Strict Environment Variable Validation
_secret_key = os.getenv("SECRET_KEY", "").strip()
_db_password = os.getenv("DB_PASSWORD")

if not _secret_key:
    raise RuntimeError(
        "FATAL CONFIGURATION ERROR: 'SECRET_KEY' environment variable is missing or empty. "
        "Define SECRET_KEY in your .env file or deployment environment."
    )

if _db_password is None:
    raise RuntimeError(
        "FATAL CONFIGURATION ERROR: 'DB_PASSWORD' environment variable is missing. "
        "Define DB_PASSWORD in your .env file or deployment environment."
    )

class Config:
    """Central Application Configuration."""
    SECRET_KEY = _secret_key
    DB_HOST = os.getenv("DB_HOST", "localhost")
    db_port_val = os.getenv("DB_PORT", "3307").strip()
    DB_PORT = int(db_port_val) if db_port_val.isdigit() else 3307
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = _db_password
    DB_NAME = os.getenv("DB_NAME", "placement_db")
    DB_SSL = os.getenv("DB_SSL", "False").lower() in ("true", "1", "yes")

    # Security: Default DEBUG to False
    DEBUG = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "yes")
    DEMO_MODE = os.getenv("DEMO_MODE", "False").lower() in ("true", "1", "yes")

    # Uploads & Size Limits
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB max request size

    # Session Cookie Security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("FLASK_ENV", "").lower() == "production" or os.getenv("COOKIE_SECURE", "False").lower() in ("true", "1")
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)

    # Google OAuth 2.0 Credentials (Optional)
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "").strip()
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "").strip()

    # Rate Limiting
    RATELIMIT_DEFAULT = "200 per day;50 per hour"
    RATELIMIT_STORAGE_URI = "memory://"
