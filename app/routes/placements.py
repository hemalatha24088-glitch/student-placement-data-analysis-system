"""
Placement Records Blueprint.
Provides placement offers CRUD, duplicate enforcement, package validation, and filtering.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.services.placement_service import (
    get_placements,
    get_placement_by_id,
    create_placement,
    update_placement,
    delete_placement,
    VALID_STATUSES,
    VALID_OFFER_TYPES
)
from app.services.student_service import get_all_departments, get_all_graduation_years, get_students
from app.services.company_service import get_companies

placements_bp = Blueprint("placements", __name__, url_prefix="/placements")

@placements_bp.route("/")
def list_placements():
    page = request.args.get("page", 1, type=int)
    dept = request.args.get("department", "All")
    year = request.args.get("graduation_year", "All")
    comp_id = request.args.get("company_id", "All")
    status = request.args.get("status", "All")
    search = request.args.get("search", "").strip()

    result = get_placements(
        department=dept,
        graduation_year=year,
        company_id=comp_id,
        status=status,
        search=search,
        page=page,
        per_page=12
    )

    departments = get_all_departments()
    graduation_years = get_all_graduation_years()
    companies = get_companies()

    return render_template(
        "placements/index.html",
        placements=result["placements"],
        total=result["total"],
        page=result["page"],
        per_page=result["per_page"],
        total_pages=result["total_pages"],
        departments=departments,
        graduation_years=graduation_years,
        companies=companies,
        statuses=VALID_STATUSES,
        selected_dept=dept,
        selected_year=year,
        selected_company=comp_id,
        selected_status=status,
        search=search
    )

@placements_bp.route("/add", methods=["GET", "POST"])
def add_placement():
    if request.method == "POST":
        data = {
            "student_id": request.form.get("student_id"),
            "company_id": request.form.get("company_id"),
            "role": request.form.get("role"),
            "package_amount": request.form.get("package_amount"),
            "package_unit": request.form.get("package_unit", "LPA"),
            "placement_date": request.form.get("placement_date"),
            "placement_year": request.form.get("placement_year"),
            "status": request.form.get("status"),
            "offer_type": request.form.get("offer_type"),
            "notes": request.form.get("notes")
        }
        success, result = create_placement(data)
        if success:
            flash("Placement record successfully added!", "success")
            return redirect(url_for("placements.list_placements"))
        else:
            flash(result, "danger")

    # Fetch eligible students and companies for dropdown
    all_students_res = get_students(per_page=200, eligibility="1")
    companies = get_companies()
    return render_template(
        "placements/form.html",
        placement=None,
        students=all_students_res["students"],
        companies=companies,
        statuses=VALID_STATUSES,
        offer_types=VALID_OFFER_TYPES,
        action="Add"
    )

@placements_bp.route("/<int:placement_id>/edit", methods=["GET", "POST"])
def edit_placement(placement_id):
    placement = get_placement_by_id(placement_id)
    if not placement:
        flash("Placement record not found.", "warning")
        return redirect(url_for("placements.list_placements"))

    if request.method == "POST":
        data = {
            "student_id": request.form.get("student_id"),
            "company_id": request.form.get("company_id"),
            "role": request.form.get("role"),
            "package_amount": request.form.get("package_amount"),
            "package_unit": request.form.get("package_unit", "LPA"),
            "placement_date": request.form.get("placement_date"),
            "placement_year": request.form.get("placement_year"),
            "status": request.form.get("status"),
            "offer_type": request.form.get("offer_type"),
            "notes": request.form.get("notes")
        }
        success, result = update_placement(placement_id, data)
        if success:
            flash("Placement offer updated successfully!", "success")
            return redirect(url_for("placements.list_placements"))
        else:
            flash(result, "danger")

    all_students_res = get_students(per_page=200)
    companies = get_companies()
    return render_template(
        "placements/form.html",
        placement=placement,
        students=all_students_res["students"],
        companies=companies,
        statuses=VALID_STATUSES,
        offer_types=VALID_OFFER_TYPES,
        action="Edit"
    )

@placements_bp.route("/<int:placement_id>/delete", methods=["POST"])
def remove_placement(placement_id):
    placement = get_placement_by_id(placement_id)
    if not placement:
        flash("Placement not found.", "warning")
        return redirect(url_for("placements.list_placements"))

    if delete_placement(placement_id):
        flash("Placement offer record removed.", "info")
    else:
        flash("Could not delete placement record.", "danger")
    return redirect(url_for("placements.list_placements"))
