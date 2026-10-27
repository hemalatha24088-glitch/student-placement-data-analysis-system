"""Flask application entrypoint and Vercel Serverless entrypoint."""

import os
import sys

# Ensure root directory is in sys.path
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import create_app  # noqa: E402
from config import Config  # noqa: E402

# Expose top-level application instance for WSGI / ASGI / Vercel Serverless runtime
app = create_app(Config)
application = app
handler = app

if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", 5000))
    app.run(host=host, port=port, debug=app.config.get("DEBUG", False))
