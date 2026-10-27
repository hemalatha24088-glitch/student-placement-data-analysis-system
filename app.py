"""Flask application entrypoint and Vercel Serverless entrypoint."""

import os
import sys

# Ensure root directory is in sys.path
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

try:
    from app import create_app
    from config import Config

    app = create_app(Config)
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
    <h1>Configuration Notice</h1>
    <p>Your Vercel deployment is active, but required database environment variables are missing:</p>
    <pre>{error_details}</pre>
    <h3>How to configure in 1 minute:</h3>
    <ol>
      <li>Go to your <a href="https://vercel.com/dashboard" target="_blank" rel="noopener">Vercel Dashboard</a>.</li>
      <li>Click on this project &rarr; <b>Settings</b> &rarr; <b>Environment Variables</b>.</li>
      <li>Add:
        <ul>
          <li><code>SECRET_KEY</code></li>
          <li><code>DB_HOST</code></li>
          <li><code>DB_PORT</code></li>
          <li><code>DB_USER</code></li>
          <li><code>DB_PASSWORD</code></li>
          <li><code>DB_NAME</code></li>
          <li><code>DB_SSL</code> (set to <code>true</code>)</li>
          <li><code>DEMO_MODE</code> (set to <code>true</code>)</li>
        </ul>
      </li>
      <li>Go to <b>Deployments</b> &rarr; click <b>Redeploy</b>.</li>
    </ol>
  </div>
</body>
</html>""",
            500,
        )


if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", 5000))
    app.run(host=host, port=port)
