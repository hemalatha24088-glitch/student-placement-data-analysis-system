"""
Data Import Blueprint.
Allows uploading students and placements via CSV with full validation,
secure filename sanitization, row caps, and RBAC protection.
"""

from flask import Blueprint, Response, flash, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

from app.services.import_service import (
    generate_placement_csv_template,
    generate_student_csv_template,
    import_placements_csv,
    import_students_csv,
)
from app.utils.auth import role_required

import_bp = Blueprint("import_bp", __name__, url_prefix="/import")
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


@import_bp.route("/")
@role_required("admin", "placement_officer")
def index():
    return render_template("import/index.html")


@import_bp.route("/students", methods=["POST"])
@role_required("admin", "placement_officer")
def upload_students():
    if "csv_file" not in request.files:
        flash("No file part provided in upload.", "danger")
        return redirect(url_for("import_bp.index"))

    file = request.files["csv_file"]
    if not file or file.filename == "":
        flash("No file selected for upload.", "danger")
        return redirect(url_for("import_bp.index"))

    filename = secure_filename(file.filename)
    if not filename.lower().endswith(".csv"):
        flash("File must be a valid .csv spreadsheet.", "danger")
        return redirect(url_for("import_bp.index"))

    content = file.stream.read()
    if len(content) > MAX_FILE_SIZE:
        flash("CSV file size exceeds 5MB limit.", "danger")
        return redirect(url_for("import_bp.index"))

    try:
        stream = content.decode("utf-8-sig").splitlines()
        result = import_students_csv(stream)
        if not result.get("success"):
            flash(result.get("message", "Import failed."), "danger")
            return redirect(url_for("import_bp.index"))

        return render_template("import/result.html", result=result, import_type="Students")
    except Exception as e:
        flash(f"Error processing CSV: {str(e)}", "danger")
        return redirect(url_for("import_bp.index"))


@import_bp.route("/placements", methods=["POST"])
@role_required("admin", "placement_officer")
def upload_placements():
    if "csv_file" not in request.files:
        flash("No file part provided in upload.", "danger")
        return redirect(url_for("import_bp.index"))

    file = request.files["csv_file"]
    if not file or file.filename == "":
        flash("No file selected for upload.", "danger")
        return redirect(url_for("import_bp.index"))

    filename = secure_filename(file.filename)
    if not filename.lower().endswith(".csv"):
        flash("File must be a valid .csv spreadsheet.", "danger")
        return redirect(url_for("import_bp.index"))

    content = file.stream.read()
    if len(content) > MAX_FILE_SIZE:
        flash("CSV file size exceeds 5MB limit.", "danger")
        return redirect(url_for("import_bp.index"))

    try:
        stream = content.decode("utf-8-sig").splitlines()
        result = import_placements_csv(stream)
        if not result.get("success"):
            flash(result.get("message", "Import failed."), "danger")
            return redirect(url_for("import_bp.index"))

        return render_template("import/result.html", result=result, import_type="Placements")
    except Exception as e:
        flash(f"Error processing CSV: {str(e)}", "danger")
        return redirect(url_for("import_bp.index"))


@import_bp.route("/template/<template_type>")
@role_required("admin", "placement_officer")
def download_template(template_type):
    if template_type == "students":
        csv_data = generate_student_csv_template()
        filename = "students_template.csv"
    else:
        csv_data = generate_placement_csv_template()
        filename = "placements_template.csv"

    return Response(csv_data, mimetype="text/csv", headers={"Content-Disposition": f"attachment; filename={filename}"})
