"""
Deep Analytics Blueprint.
Provides dedicated analytical breakdowns:
- Department-Wise Analysis
- Salary Package Analysis
- Skills Correlation Analysis
- Historical Graduation Trends
"""
from flask import Blueprint, render_template, request
from app.services.analytics_service import (
    get_kpis,
    get_department_analytics,
    get_package_analytics,
    get_skill_analytics,
    get_yearly_trends,
    generate_placement_insights
)
from app.services.student_service import get_all_departments, get_all_graduation_years
from app.services.company_service import get_companies

analytics_bp = Blueprint("analytics", __name__, url_prefix="/analytics")

@analytics_bp.route("/")
def index():
    """Analytics Hub redirecting or summarizing modules."""
    year = request.args.get("graduation_year", "All")
    dept = request.args.get("department", "All")
    kpis = get_kpis(department=dept, graduation_year=year)
    depts = get_department_analytics(graduation_year=year)
    pkg = get_package_analytics(department=dept, graduation_year=year)
    insights = generate_placement_insights(department=dept, graduation_year=year)
    departments = get_all_departments()
    years = get_all_graduation_years()

    return render_template(
        "analytics/overview.html",
        kpis=kpis,
        depts=depts,
        pkg=pkg,
        insights=insights,
        departments=departments,
        years=years,
        selected_dept=dept,
        selected_year=year
    )

@analytics_bp.route("/departments")
def departments_analysis():
    """Detailed Department-Wise Placement Performance."""
    year = request.args.get("graduation_year", "All")
    dept_data = get_department_analytics(graduation_year=year)
    years = get_all_graduation_years()
    return render_template("analytics/departments.html", dept_data=dept_data, years=years, selected_year=year)

@analytics_bp.route("/packages")
def packages_analysis():
    """Detailed Salary Package Distribution & Tiers."""
    dept = request.args.get("department", "All")
    year = request.args.get("graduation_year", "All")
    pkg_data = get_package_analytics(department=dept, graduation_year=year)
    departments = get_all_departments()
    years = get_all_graduation_years()
    return render_template(
        "analytics/packages.html",
        pkg=pkg_data,
        departments=departments,
        years=years,
        selected_dept=dept,
        selected_year=year
    )

@analytics_bp.route("/skills")
def skills_analysis():
    """Skills recorded among placed vs unplaced candidates."""
    dept = request.args.get("department", "All")
    skills_data = get_skill_analytics(department=dept)
    departments = get_all_departments()
    return render_template("analytics/skills.html", skills=skills_data, departments=departments, selected_dept=dept)

@analytics_bp.route("/trends")
def trends_analysis():
    """Multi-year progression across graduation classes."""
    trends = get_yearly_trends()
    return render_template("analytics/trends.html", trends=trends)
