"""Flask application entrypoint and Vercel Serverless entrypoint."""

import os
import sys

# Ensure root directory is in sys.path
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Top-level declarations ensure Vercel static AST analyzer always discovers the entrypoint
app = None
application = None
handler = None

try:
    from app import create_app  # noqa: E402
    from config import Config  # noqa: E402

    # Instantiate the primary production Flask application
    app = create_app(Config)
    application = app
    handler = app

except Exception as exc:
    from flask import Flask  # noqa: E402

    # Diagnostic fallback app shown when required environment variables are missing
    app = Flask(__name__)
    application = app
    handler = app
    _error_details = str(exc)

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def configuration_notice(path):
        return (
            f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Configuration Required | Student Placement System</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; display: flex; align-items: center; justify-content: center; min-height: 100vh; margin: 0; padding: 20px; box-sizing: border-box; }}
    .card {{ background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 32px; max-width: 650px; width: 100%; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.5); }}
    h1 {{ color: #f87171; font-size: 1.4rem; margin-top: 0; }}
    pre {{ background: #090d16; color: #fca5a5; padding: 14px; border-radius: 8px; font-size: 0.85rem; overflow-x: auto; border: 1px solid #7f1d1d; white-space: pre-wrap; }}
    ol {{ padding-left: 20px; line-height: 1.6; color: #cbd5e1; }}
    code {{ background: #334155; color: #38bdf8; padding: 2px 6px; border-radius: 4px; font-size: 0.85rem; }}
    a {{ color: #818cf8; text-decoration: none; font-weight: 600; }}
    a:hover {{ text-decoration: underline; }}
    .info {{ background: #1e3a5f; border-left: 4px solid #38bdf8; padding: 12px; border-radius: 4px; margin-bottom: 16px; font-size: 0.9rem; color: #bae6fd; }}
  </style>
</head>
<body>
  <div class="card">
    <h1>Configuration Required</h1>
    <div class="info">
      Your Vercel deployment built successfully, but required production environment variables are missing.
    </div>
    <pre>{_error_details}</pre>
    <h3>How to configure in 1 minute:</h3>
    <ol>
      <li>Go to your <a href="https://vercel.com/dashboard" target="_blank" rel="noopener">Vercel Dashboard</a>.</li>
      <li>Click on this project &rarr; <b>Settings</b> &rarr; <b>Environment Variables</b>.</li>
      <li>Add the following variables:
        <ul>
          <li><code>SECRET_KEY</code> (a random 32+ character string)</li>
          <li><code>DB_HOST</code> (your MySQL host, e.g. Aiven, Railway, TiDB, or PlanetScale)</li>
          <li><code>DB_PORT</code> (e.g. <code>3306</code>)</li>
          <li><code>DB_USER</code> (your database username)</li>
          <li><code>DB_PASSWORD</code> (your database password)</li>
          <li><code>DB_NAME</code> (e.g. <code>placement_db</code>)</li>
          <li><code>DB_SSL</code> (set to <code>true</code> for cloud databases)</li>
          <li><code>DEMO_MODE</code> (set to <code>true</code> to enable 1-click test logins)</li>
        </ul>
      </li>
      <li>Go to <b>Deployments</b> &rarr; click <b>Redeploy</b> (or push a new commit).</li>
    </ol>
  </div>
</body>
</html>""",
            500,
        )


if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", 5000))
    app.run(host=host, port=port, debug=app.config.get("DEBUG", False))
