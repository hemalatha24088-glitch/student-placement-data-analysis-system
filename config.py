import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-placement-analytics-2026")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    db_port_val = os.getenv("DB_PORT", "3307").strip()
    DB_PORT = int(db_port_val) if db_port_val.isdigit() else 3307
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "aimlb4")
    DB_NAME = os.getenv("DB_NAME", "placement_db")
    DB_SSL = os.getenv("DB_SSL", "False").lower() in ("true", "1", "yes")
    DEBUG = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "yes")
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
