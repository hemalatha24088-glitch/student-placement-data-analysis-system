"""
WSGI entrypoint for production deployment.
Compatible with Gunicorn, Waitress, uWSGI, Render, Railway, AWS, and Docker.
"""
import os
from app import create_app

app = create_app()

if __name__ == "__main__":
    from waitress import serve
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")
    print("\n=======================================================")
    print(f" Production WSGI Server (Waitress) active on http://{host}:{port}")
    print(" Press CTRL+C to stop.")
    print("=======================================================\n")
    serve(app, host=host, port=port, threads=6)
