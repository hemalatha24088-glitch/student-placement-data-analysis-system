"""
Root application runner for Student Placement Data Analysis System.
Run via: python run.py
"""
import os
from app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("\n=======================================================")
    print(" STUDENT PLACEMENT DATA ANALYSIS SYSTEM")
    print(f" Local Web Server Running at: http://127.0.0.1:{port}/")
    print(" Press CTRL+C to stop.")
    print("=======================================================\n")
    app.run(host="127.0.0.1", port=port, debug=True)
