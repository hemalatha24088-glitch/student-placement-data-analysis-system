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


@api_bp.route("/chart-data")
def chart_data():
    """Returns structured JSON datasets for interactive Chart.js visualizations."""
    from app.services.company_service import get_companies

    dept = request.args.get("department", "All")
    year = request.args.get("graduation_year", "All")

    dept_analytics = get_department_analytics(graduation_year=year)
    departments = [d["department"] for d in dept_analytics]
    placement_rates = [d["placement_rate"] for d in dept_analytics]
    eligible_students = [d["eligible_students"] for d in dept_analytics]
    placed_students = [d["placed_students"] for d in dept_analytics]
    unplaced_students = [d["unplaced_students"] for d in dept_analytics]

    pkg_analytics = get_package_analytics(department=dept, graduation_year=year)

    skill_analytics = get_skill_analytics(department=dept)[:10]
    skills_labels = [s["skill_name"] for s in skill_analytics]
    skills_placed = [s["placed_students_with_skill"] for s in skill_analytics]
    skills_total = [s["total_students_with_skill"] for s in skill_analytics]

    companies = get_companies()[:8]
    company_names = [c["company_name"] for c in companies]
    company_offers = [c["total_offers"] for c in companies]
    company_avg_ctc = [float(c["avg_package_lpa"] or 0) for c in companies]

    trends = get_yearly_trends()
    trend_years = [str(t.get("graduation_year") or t.get("year", "")) for t in trends]
    trend_placed = [t.get("placed_students") or t.get("placed", 0) for t in trends]
    trend_rates = [t.get("placement_rate") or t.get("rate", 0.0) for t in trends]
    trend_avg_ctc = [float(t.get("avg_package_lpa") or t.get("avg_package") or 0) for t in trends]

    return jsonify(
        {
            "success": True,
            "filters": {"department": dept, "graduation_year": year},
            "dept_rates": {
                "labels": departments,
                "rates": placement_rates,
                "eligible": eligible_students,
                "placed": placed_students,
                "unplaced": unplaced_students,
            },
            "package_stats": pkg_analytics,
            "skills": {
                "labels": skills_labels,
                "placed": skills_placed,
                "total": skills_total,
            },
            "companies": {
                "labels": company_names,
                "offers": company_offers,
                "avg_ctc": company_avg_ctc,
            },
            "trends": {
                "labels": trend_years,
                "placed": trend_placed,
                "rates": trend_rates,
                "avg_ctc": trend_avg_ctc,
            },
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
