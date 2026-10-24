"""
Flask application entrypoint.
"""
import os
from app import create_app
from config import Config

app = create_app(Config)

if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", 5000))
    app.run(host=host, port=port, debug=app.config.get("DEBUG", False))
