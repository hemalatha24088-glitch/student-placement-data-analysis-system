"""Vercel Serverless Function entrypoint for Student Placement Data Analysis System.

Exposes the Flask WSGI application instance 'app' for Vercel's Python runtime.
"""

import os
import sys

# Add root directory to Python path so 'app' and 'config' can be imported
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

try:
    from app import create_app

    app = create_app()
except Exception as exc:
    from flask import Flask

    app = Flask(__name__)
    error_details = str(exc)

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def configuration_notice(path):
        return (
            f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Vercel Configuration Notice | Student Placement System</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; display: flex; align-items: center; justify-content: center; min-height: 100vh; margin: 0; padding: 20px; box-sizing: border-box; }}
    .card {{ background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 32px; max-width: 600px; width: 100%; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.5); }}
    h1 {{ color: #f87171; font-size: 1.4rem; margin-top: 0; }}
    pre {{ background: #090d16; color: #fca5a5; padding: 14px; border-radius: 8px; font-size: 0.85rem; overflow-x: auto; border: 1px solid #7f1d1d; }}
    ol {{ padding-left: 20px; line-height: 1.6; color: #cbd5e1; }}
    code {{ background: #334155; color: #38bdf8; padding: 2px 6px; border-radius: 4px; font-size: 0.85rem; }}
    a {{ color: #818cf8; text-decoration: none; font-weight: 600; }}
    a:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>
  <div class="card">
    <h1>Configuration Required on Vercel</h1>
    <p>Your Vercel deployment was initiated successfully, but required cloud environment variables are missing:</p>
    <pre>{error_details}</pre>
    <h3>How to configure in 1 minute:</h3>
    <ol>
      <li>Open your <a href="https://vercel.com/dashboard" target="_blank" rel="noopener">Vercel Dashboard</a>.</li>
      <li>Click on your project &rarr; <b>Settings</b> &rarr; <b>Environment Variables</b>.</li>
      <li>Add the following keys:
        <ul>
          <li><code>SECRET_KEY</code>: A strong random 32+ character string</li>
          <li><code>DB_HOST</code>: Your cloud MySQL host (e.g. Aiven, TiDB Cloud, Railway)</li>
          <li><code>DB_PORT</code>: Your cloud MySQL port (e.g. <code>3306</code>)</li>
          <li><code>DB_USER</code>: Your cloud MySQL user</li>
          <li><code>DB_PASSWORD</code>: Your cloud MySQL password</li>
          <li><code>DB_NAME</code>: <code>placement_db</code></li>
          <li><code>DB_SSL</code>: <code>true</code></li>
          <li><code>DEMO_MODE</code>: <code>true</code> (optional, enables 1-click evaluator login)</li>
        </ul>
      </li>
      <li>Navigate to <b>Deployments</b> and click <b>Redeploy</b>.</li>
    </ol>
  </div>
</body>
</html>""",
            500,
        )


# For local invocation testing
if __name__ == "__main__":
    app.run()
