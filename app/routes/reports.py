"""
Reports Blueprint.
Generates comprehensive printable placement reports and dynamic CSV downloads.
"""
import io
import csv
from datetime import datetime
from flask import Blueprint, render_template, request, Response
from app.services.analytics_service import (
    get_kpis,
    get_department_analytics,
    get_package_analytics,
    get_skill_analytics,
    load_placement_dataframe
)
from app.services.company_service import get_companies
from app.services.student_service import get_all_departments, get_all_graduation_years

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")

@reports_bp.route("/")
def index():
    report_type = request.args.get("type", "summary")
    dept = request.args.get("department", "All")
    year = request.args.get("graduation_year", "All")

    departments = get_all_departments()
    years = get_all_graduation_years()
    generated_at = datetime.now().strftime("%d %B %Y, %I:%M %p")

    context = {
        "report_type": report_type,
        "selected_dept": dept,
        "selected_year": year,
        "departments": departments,
        "years": years,
        "generated_at": generated_at
    }

    if report_type == "summary":
        context["kpis"] = get_kpis(department=dept, graduation_year=year)
        context["depts"] = get_department_analytics(graduation_year=year)
    elif report_type == "department":
        context["depts"] = get_department_analytics(graduation_year=year)
    elif report_type == "companies":
        context["companies"] = get_companies()
    elif report_type == "skills":
        context["skills"] = get_skill_analytics(department=dept)
    elif report_type == "packages":
        context["pkg"] = get_package_analytics(department=dept, graduation_year=year)
    elif report_type == "students":
        df = load_placement_dataframe(department=dept, graduation_year=year)
        context["student_rows"] = df.to_dict(orient="records") if not df.empty else []

    return render_template("reports/index.html", **context)

@reports_bp.route("/export-csv")
def export_csv():
    report_type = request.args.get("type", "summary")
    dept = request.args.get("department", "All")
    year = request.args.get("graduation_year", "All")

    output = io.StringIO()
    writer = csv.writer(output)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"placement_{report_type}_report_{timestamp}.csv"

    if report_type == "summary":
        kpis = get_kpis(department=dept, graduation_year=year)
        writer.writerow(["Metric", "Value", "Notes"])
        writer.writerow(["Total Registered Students", kpis["total_students"], "Distinct students in database"])
        writer.writerow(["Total Eligible Students", kpis["total_eligible"], "Students eligible for placement"])
        writer.writerow(["Distinct Placed Students", kpis["total_placed"], "Confirmed placed offers"])
        writer.writerow(["Unplaced Eligible Students", kpis["unplaced_students"], "Eligible - Placed"])
        writer.writerow(["Overall Placement Rate (%)", f"{kpis['placement_rate']}%", "Placed / Eligible * 100"])
        writer.writerow(["Average Package (LPA)", f"{kpis['avg_package']} LPA", "Mean of placed offers"])
        writer.writerow(["Median Package (LPA)", f"{kpis['median_package']} LPA", "Median of placed offers"])
        writer.writerow(["Highest Package (LPA)", f"{kpis['highest_package']} LPA", "Peak campus CTC offer"])
        writer.writerow(["Active Hiring Companies", kpis["total_companies"], "Companies with student placements"])

    elif report_type == "department":
        depts = get_department_analytics(graduation_year=year)
        writer.writerow(["Department", "Total Students", "Eligible", "Placed", "Unplaced", "Placement Rate (%)", "Avg CTC (LPA)", "Median CTC (LPA)", "Max CTC (LPA)"])
        for d in depts:
            writer.writerow([
                d["department"], d["total_students"], d["eligible_students"], d["placed_students"],
                d["unplaced_students"], f"{d['placement_rate']}%", d["avg_package"], d["median_package"], d["highest_package"]
            ])

    elif report_type == "companies":
        companies = get_companies()
        writer.writerow(["Company Name", "Industry", "Location", "Tier", "Total Offers", "Distinct Hires", "Avg CTC (LPA)", "Max CTC (LPA)"])
        for c in companies:
            writer.writerow([
                c["company_name"], c["industry"], c["location"], c["tier"],
                c["total_offers"], c["distinct_students_hired"], c["avg_package_lpa"] or "N/A", c["max_package_lpa"] or "N/A"
            ])

    elif report_type == "skills":
        skills = get_skill_analytics(department=dept)
        writer.writerow(["Skill Name", "Category", "Total Students with Skill", "Placed Students with Skill", "Unplaced Students with Skill"])
        for s in skills:
            writer.writerow([
                s["skill_name"], s["skill_category"], s["total_students_with_skill"],
                s["placed_students_with_skill"], s["unplaced_students_with_skill"]
            ])

    elif report_type == "packages":
        pkg = get_package_analytics(department=dept, graduation_year=year)
        writer.writerow(["Salary Package Metric", "Value (LPA)"])
        writer.writerow(["Number of Placed Offers", pkg["count"]])
        writer.writerow(["Mean Package", pkg["mean"]])
        writer.writerow(["Median Package", pkg["median"]])
        writer.writerow(["Standard Deviation", pkg["std"]])
        writer.writerow(["Minimum Package", pkg["min"]])
        writer.writerow(["Maximum Package", pkg["max"]])
        writer.writerow(["25th Percentile", pkg["p25"]])
        writer.writerow(["75th Percentile", pkg["p75"]])
        writer.writerow(["90th Percentile", pkg["p90"]])

    elif report_type == "students":
        df = load_placement_dataframe(department=dept, graduation_year=year)
        if not df.empty:
            cols = ["roll_no", "student_name", "department", "graduation_year", "cgpa", "eligible_for_placement", "company_name", "role", "package_amount", "package_unit", "placement_status"]
            export_df = df[cols].fillna("N/A")
            writer.writerow(["Roll No", "Student Name", "Department", "Graduation Year", "CGPA", "Eligible (1/0)", "Company", "Role", "Package", "Unit", "Status"])
            for _, r in export_df.iterrows():
                writer.writerow(list(r))
        else:
            writer.writerow(["No student records found."])

    csv_data = output.getvalue()
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
