"""
Main Blueprint.
Handles Landing Page, Main Analytics Dashboard, and System Health Check.
"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session
from app.utils.auth import login_required
from app.services.analytics_service import (
    get_kpis,
    get_department_analytics,
    get_package_analytics,
    get_skill_analytics,
    generate_placement_insights
)
from app.services.student_service import get_all_departments, get_all_graduation_years
from app.services.company_service import get_companies
from app.services.placement_service import get_recent_placements
from app.database.connection import check_db_health

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    """Root entry point: Require sign-in first before opening the system."""
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))
    return redirect(url_for("main.dashboard"))

@main_bp.route("/overview")
@login_required
def overview():
    """System Overview & Project Features Presentation (accessible after login)."""
    kpis = get_kpis()
    departments = get_all_departments()
    return render_template("index.html", kpis=kpis, departments=departments)

@main_bp.route("/model-info")
@login_required
def model_info_alias():
    """Direct root endpoint to Model Performance and Diagnostics portal."""
    from app.routes.predictor import model_info
    return model_info()

@main_bp.route("/dashboard")
@login_required
def dashboard():
    """Main Analytics Dashboard with interactive global filters."""
    dept = request.args.get("department", "All")
    year = request.args.get("graduation_year", "All")
    status = request.args.get("status", "All")
    company_id = request.args.get("company_id", "All")

    # Fetch dynamic analytics based on filters
    kpis = get_kpis(department=dept, graduation_year=year, company_id=company_id, status=status)
    insights = generate_placement_insights(department=dept, graduation_year=year)
    recent_placements = get_recent_placements(limit=6)
    dept_summary = get_department_analytics(graduation_year=year)
    skills_summary = get_skill_analytics(department=dept)[:6]
    top_companies = get_companies()[:5]

    # Filter dropdown options
    departments = get_all_departments()
    graduation_years = get_all_graduation_years()
    companies = get_companies()

    return render_template(
        "dashboard.html",
        kpis=kpis,
        insights=insights,
        recent_placements=recent_placements,
        dept_summary=dept_summary,
        skills_summary=skills_summary,
        top_companies=top_companies,
        departments=departments,
        graduation_years=graduation_years,
        companies=companies,
        selected_dept=dept,
        selected_year=year,
        selected_status=status,
        selected_company=company_id
    )

@main_bp.route("/health")
def health_page():
    """HTML health check page showing database status and diagnostics."""
    health_data = check_db_health()
    return render_template("health.html", health=health_data)

@main_bp.route("/api/health")
def health_api():
    """JSON health check endpoint."""
    health_data = check_db_health()
    status_code = 200 if health_data["connected"] else 503
    return jsonify(health_data), status_code
