"""
Application Factory for Student Placement Data Analysis System.
Configures security extensions, blueprints, error handlers, and context processors.
"""

import os

from authlib.integrations.flask_client import OAuth
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix

from app.limiter import limiter
from config import Config

csrf = CSRFProtect()
oauth = OAuth()
talisman = Talisman()


def create_app(config_class=Config):
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(config_class)

    # Wrap WSGI application with ProxyFix to properly handle X-Forwarded-* headers from reverse proxies
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    # Ensure upload and log directories exist (handling serverless read-only filesystems)
    is_serverless = os.environ.get("VERCEL") == "1" or os.environ.get("AWS_LAMBDA_FUNCTION_NAME") is not None
    upload_folder = "/tmp/uploads" if is_serverless else app.config.get("UPLOAD_FOLDER", "uploads")
    try:
        os.makedirs(upload_folder, exist_ok=True)
        app.config["UPLOAD_FOLDER"] = upload_folder
    except OSError:
        pass

    # Configure Structured Logging
    if not app.config.get("TESTING"):
        import logging

        app.logger.setLevel(logging.INFO)
        if not is_serverless:
            try:
                from logging.handlers import RotatingFileHandler

                os.makedirs("logs", exist_ok=True)
                log_file = os.path.join("logs", "app.log")
                file_handler = RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024, backupCount=5)
                file_handler.setFormatter(
                    logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s (%(process)d): %(message)s")
                )
                file_handler.setLevel(logging.INFO)
                app.logger.addHandler(file_handler)
            except OSError:
                pass
        app.logger.info("Student Placement Data Analysis System starting up.")

    # Initialize Extensions
    csrf.init_app(app)
    limiter.init_app(app)

    # Initialize Talisman (Security Headers)
    if app.config.get("TESTING"):
        talisman.init_app(app, force_https=False, content_security_policy=None)
    else:
        csp = {
            "default-src": ["'self'"],
            "script-src": [
                "'self'",
                "'unsafe-inline'",
                "'unsafe-eval'",
                "https://cdn.jsdelivr.net",
                "https://cdnjs.cloudflare.com",
            ],
            "style-src": [
                "'self'",
                "'unsafe-inline'",
                "https://cdn.jsdelivr.net",
                "https://cdnjs.cloudflare.com",
                "https://fonts.googleapis.com",
            ],
            "font-src": ["'self'", "https://fonts.gstatic.com", "https://cdnjs.cloudflare.com", "data:"],
            "img-src": ["'self'", "data:", "https:"],
        }
        force_https = app.config.get("SESSION_COOKIE_SECURE", False)
        talisman.init_app(
            app,
            content_security_policy=csp,
            force_https=force_https,
            frame_options="SAMEORIGIN",
            referrer_policy="strict-origin-when-cross-origin",
        )

    # Register Google OAuth 2.0 if credentials are provided
    if app.config.get("GOOGLE_CLIENT_ID") and app.config.get("GOOGLE_CLIENT_SECRET"):
        oauth.init_app(app)
        oauth.register(
            name="google",
            client_id=app.config["GOOGLE_CLIENT_ID"],
            client_secret=app.config["GOOGLE_CLIENT_SECRET"],
            server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
            client_kwargs={"scope": "openid email profile"},
        )

    # Register Blueprints
    from app.routes.admin import admin_bp
    from app.routes.analytics import analytics_bp
    from app.routes.api import api_bp
    from app.routes.ats import ats_bp
    from app.routes.auth import auth_bp
    from app.routes.companies import companies_bp
    from app.routes.import_export import import_bp
    from app.routes.main import main_bp
    from app.routes.placements import placements_bp
    from app.routes.predictor import predictor_bp
    from app.routes.reports import reports_bp
    from app.routes.skills import skills_bp
    from app.routes.students import students_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(companies_bp)
    app.register_blueprint(skills_bp)
    app.register_blueprint(placements_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(import_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(predictor_bp)
    app.register_blueprint(ats_bp)

    # Enforce Route Protection for Unauthenticated Visitors
    @app.before_request
    def require_login_first():
        if app.config.get("TESTING"):
            return

        allowed_endpoints = {
            "auth.login",
            "auth.register",
            "auth.signup",
            "auth.demo_login",
            "auth.google_login",
            "auth.google_callback",
            "auth.logout",
            "main.health_page",
            "api.health_check",
            "static",
        }

        if request.endpoint and (request.endpoint in allowed_endpoints or request.endpoint.startswith("static")):
            return

        if request.endpoint and not session.get("user_id"):
            next_dest = url_for("main.dashboard") if request.path in ("/", "/login") else request.url
            return redirect(url_for("auth.login", next=next_dest))

    # Global Context Processor
    @app.context_processor
    def inject_security_context():
        google_enabled = bool(app.config.get("GOOGLE_CLIENT_ID") and app.config.get("GOOGLE_CLIENT_SECRET"))
        return {
            "demo_mode": app.config.get("DEMO_MODE", False),
            "google_auth_enabled": google_enabled,
            "current_user_role": session.get("role", "anonymous"),
        }

    # Custom Jinja2 Filters
    @app.template_filter("currency_lpa")
    def currency_lpa_filter(val):
        if val is None or val == "":
            return "N/A"
        try:
            return f"₹{float(val):.2f} LPA"
        except (ValueError, TypeError):
            return str(val)

    @app.template_filter("format_date")
    def format_date_filter(val, fmt="%b %d, %Y"):
        if not val:
            return "N/A"
        if hasattr(val, "strftime"):
            return val.strftime(fmt)
        return str(val)

    # Custom HTTP Error Handlers (Zero Leaked Stack Traces)
    from flask_wtf.csrf import CSRFError

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        flash("Your session security token expired or cookies were refreshed. Please sign in again.", "warning")
        return render_template("auth/login.html", next_url=url_for("main.dashboard")), 400

    @app.errorhandler(403)
    def forbidden_error(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(429)
    def ratelimit_exceeded(e):
        return render_template("errors/429.html"), 429

    @app.errorhandler(500)
    def server_error(e):
        app.logger.error(f"Internal Server Error: {str(e)}")
        return render_template("errors/500.html"), 500

    return app
