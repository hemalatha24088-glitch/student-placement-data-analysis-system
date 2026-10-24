"""
Root application runner for Student Placement Data Analysis System.
Run via: python run.py
"""
import os
from app import create_app
from config import Config

app = create_app(Config)

if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", 5000))
    debug = app.config.get("DEBUG", False)
    print("\n=======================================================")
    print(" STUDENT PLACEMENT DATA ANALYSIS SYSTEM")
    print(f" Web Server Running at: http://{host}:{port}/")
    print(f" Debug Mode: {debug} | Demo Mode: {app.config.get('DEMO_MODE', False)}")
    print(" Press CTRL+C to stop.")
    print("=======================================================\n")
    app.run(host=host, port=port, debug=debug)
