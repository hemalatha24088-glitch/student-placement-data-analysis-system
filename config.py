import os
from datetime import timedelta
from urllib.parse import unquote, urlparse

from dotenv import load_dotenv

# Load variables from .env if present
load_dotenv()

# Support DATABASE_URL / MYSQL_URL (common in cloud deployments like Aiven, Railway, Render)
_db_url = os.getenv("DATABASE_URL") or os.getenv("MYSQL_URL")
_url_user = None
_url_password = None
_url_host = None
_url_port = None
_url_name = None
_url_ssl = False

if _db_url:
    try:
        parsed = urlparse(_db_url)
        _url_user = unquote(parsed.username) if parsed.username else None
        _url_password = unquote(parsed.password) if parsed.password else None
        _url_host = parsed.hostname
        _url_port = parsed.port
        if parsed.path and len(parsed.path) > 1:
            _url_name = parsed.path.lstrip("/").split("?")[0]
        _url_ssl = "ssl" in parsed.query or "ssl-mode" in parsed.query or parsed.scheme in ("mysql+ssl", "mysqls")
    except Exception:
        pass

# Strict Environment Variable Validation
_secret_key = os.getenv("SECRET_KEY", "").strip() or "placement-data-analysis-secret-token-btech-aiml-2026"
_db_password = os.getenv("DB_PASSWORD") if os.getenv("DB_PASSWORD") is not None else _url_password

if _db_password is None:
    if os.getenv("DEMO_MODE", "False").lower() in ("true", "1", "yes"):
        _db_password = ""
    else:
        raise RuntimeError(
            "FATAL CONFIGURATION ERROR: 'DB_PASSWORD' environment variable is missing. "
            "Define DB_PASSWORD or DATABASE_URL in your deployment environment."
        )


class Config:
    """Central Application Configuration."""

    SECRET_KEY = _secret_key
    DB_HOST = os.getenv("DB_HOST", _url_host or "localhost")
    db_port_val = os.getenv("DB_PORT", str(_url_port or "3307")).strip()
    DB_PORT = int(db_port_val) if db_port_val.isdigit() else 3307
    DB_USER = os.getenv("DB_USER", _url_user or "root")
    DB_PASSWORD = _db_password
    DB_NAME = os.getenv("DB_NAME", _url_name or "placement_db")
    DB_SSL = os.getenv("DB_SSL", "True" if _url_ssl else "False").lower() in ("true", "1", "yes")

    # Security: Default DEBUG to False
    DEBUG = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "yes")
    DEMO_MODE = os.getenv("DEMO_MODE", "False").lower() in ("true", "1", "yes")

    # Uploads & Size Limits
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB max request size

    # Session Cookie Security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("FLASK_ENV", "").lower() == "production" or os.getenv(
        "COOKIE_SECURE", "False"
    ).lower() in ("true", "1")
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    WTF_CSRF_SSL_STRICT = False  # Allows smooth operation through reverse proxies and tunnels

    # Google OAuth 2.0 Credentials (Optional)
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "").strip()
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "").strip()

    # Rate Limiting
    RATELIMIT_DEFAULT = "200 per day;50 per hour"
    RATELIMIT_STORAGE_URI = "memory://"
