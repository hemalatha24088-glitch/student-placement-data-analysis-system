"""
Application Factory for Student Placement Data Analysis System.
"""
import os
from flask import Flask, render_template, request, session, redirect, url_for, flash
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__,
                template_folder="templates",
                static_folder="static")
    app.config.from_object(config_class)

    # Ensure upload directory exists
    os.makedirs(app.config.get("UPLOAD_FOLDER", "uploads"), exist_ok=True)

    # Register Blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.students import students_bp
    from app.routes.companies import companies_bp
    from app.routes.skills import skills_bp
    from app.routes.placements import placements_bp
    from app.routes.analytics import analytics_bp
    from app.routes.reports import reports_bp
    from app.routes.import_export import import_bp
    from app.routes.api import api_bp
    from app.routes.predictor import predictor_bp
    from app.routes.ats import ats_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
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

    # Route Protection: Enforce Login First for internal pages
    @app.before_request
    def require_login_first():
        if app.config.get("TESTING"):
            return

        allowed_endpoints = {
            "auth.login",
            "auth.demo_login",
            "auth.logout",
            "main.index",
            "main.health_page",
            "static"
        }

        if request.endpoint and (request.endpoint in allowed_endpoints or request.endpoint.startswith("static")):
            return

        if request.endpoint and not session.get("user_id"):
            flash("Please sign in first to access the placement system.", "warning")
            return redirect(url_for("auth.login", next=request.url))

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

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("errors/500.html", error=str(e)), 500

    return app
