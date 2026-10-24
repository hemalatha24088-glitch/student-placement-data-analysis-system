"""
REST API Blueprint.
Provides JSON analytics endpoints and dynamic chart streaming.
"""

from flask import Blueprint, Response, jsonify, request

from app.services.analytics_service import (
    get_department_analytics,
    get_kpis,
    get_package_analytics,
    get_skill_analytics,
    get_yearly_trends,
)
from app.services.chart_service import (
    generate_company_recruitment_chart,
    generate_dept_placement_rate_chart,
    generate_package_distribution_chart,
    generate_placed_vs_eligible_chart,
    generate_top_skills_chart,
    generate_yearly_trends_chart,
)

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/stats")
def stats():
    dept = request.args.get("department", "All")
    year = request.args.get("graduation_year", "All")
    comp_id = request.args.get("company_id", "All")
    status = request.args.get("status", "All")

    kpis = get_kpis(department=dept, graduation_year=year, company_id=comp_id, status=status)
    return jsonify(
        {
            "success": True,
            "filters": {"department": dept, "graduation_year": year, "company_id": comp_id, "status": status},
            "kpis": kpis,
        }
    )


@api_bp.route("/charts/<chart_name>")
def stream_chart(chart_name):
    dept = request.args.get("department", "All")
    year = request.args.get("graduation_year", "All")

    if chart_name == "dept-rate":
        png_bytes = generate_dept_placement_rate_chart(graduation_year=year)
    elif chart_name == "placed-vs-eligible":
        png_bytes = generate_placed_vs_eligible_chart(graduation_year=year)
    elif chart_name == "package-distribution":
        png_bytes = generate_package_distribution_chart(department=dept, graduation_year=year)
    elif chart_name == "top-skills":
        png_bytes = generate_top_skills_chart(department=dept)
    elif chart_name in ("company-recruitment", "company-hires"):
        png_bytes = generate_company_recruitment_chart()
    elif chart_name == "yearly-trends":
        png_bytes = generate_yearly_trends_chart()
    else:
        return jsonify({"error": "Unknown chart name"}), 404

    return Response(png_bytes, mimetype="image/png")
