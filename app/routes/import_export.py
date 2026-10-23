"""
Data Import Blueprint.
Allows uploading students and placements via CSV with full validation and feedback.
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, Response
from app.services.import_service import (
    import_students_csv,
    import_placements_csv,
    generate_student_csv_template,
    generate_placement_csv_template
)

import_bp = Blueprint("import_bp", __name__, url_prefix="/import")

@import_bp.route("/")
def index():
    return render_template("import/index.html")

@import_bp.route("/students", methods=["POST"])
def upload_students():
    if "csv_file" not in request.files:
        flash("No file part provided in upload.", "danger")
        return redirect(url_for("import_bp.index"))

    file = request.files["csv_file"]
    if file.filename == "":
        flash("No file selected.", "danger")
        return redirect(url_for("import_bp.index"))

    if not file.filename.endswith(".csv"):
        flash("File must be a valid .csv spreadsheet.", "danger")
        return redirect(url_for("import_bp.index"))

    try:
        stream = file.stream.read().decode("utf-8-sig").splitlines()
        result = import_students_csv(stream)
        if not result.get("success"):
            flash(result.get("message", "Import failed."), "danger")
            return redirect(url_for("import_bp.index"))

        return render_template("import/result.html", result=result, import_type="Students")
    except Exception as e:
        flash(f"Error processing CSV: {str(e)}", "danger")
        return redirect(url_for("import_bp.index"))

@import_bp.route("/placements", methods=["POST"])
def upload_placements():
    if "csv_file" not in request.files:
        flash("No file part provided in upload.", "danger")
        return redirect(url_for("import_bp.index"))

    file = request.files["csv_file"]
    if file.filename == "":
        flash("No file selected.", "danger")
        return redirect(url_for("import_bp.index"))

    if not file.filename.endswith(".csv"):
        flash("File must be a valid .csv spreadsheet.", "danger")
        return redirect(url_for("import_bp.index"))

    try:
        stream = file.stream.read().decode("utf-8-sig").splitlines()
        result = import_placements_csv(stream)
        if not result.get("success"):
            flash(result.get("message", "Import failed."), "danger")
            return redirect(url_for("import_bp.index"))

        return render_template("import/result.html", result=result, import_type="Placements")
    except Exception as e:
        flash(f"Error processing CSV: {str(e)}", "danger")
        return redirect(url_for("import_bp.index"))

@import_bp.route("/template/<template_type>")
def download_template(template_type):
    if template_type == "students":
        csv_data = generate_student_csv_template()
        filename = "students_template.csv"
    else:
        csv_data = generate_placement_csv_template()
        filename = "placements_template.csv"

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
