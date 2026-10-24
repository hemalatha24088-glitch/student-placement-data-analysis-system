"""
Vercel Serverless Function entrypoint for Student Placement Data Analysis System.
Exposes the Flask WSGI application instance 'app' for Vercel's Python runtime.
"""
import sys
import os

# Add root directory to Python path so 'app' and 'config' can be imported
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import create_app

app = create_app()

# For local invocation testing
if __name__ == "__main__":
    app.run()
