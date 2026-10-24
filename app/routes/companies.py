"""
Company Management Blueprint.
Provides CRUD for recruiting partner companies and recruitment aggregation.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.services.company_service import (
    get_companies,
    get_company_by_id,
    create_company,
    update_company,
    delete_company,
    get_all_industries
)
from app.utils.auth import login_required, role_required

companies_bp = Blueprint("companies", __name__, url_prefix="/companies")

@companies_bp.route("/")
@login_required
def list_companies():
    search = request.args.get("search", "").strip()
    industry = request.args.get("industry", "All")
    companies = get_companies(search=search, industry=industry)
    industries = get_all_industries()
    return render_template("companies/index.html", companies=companies, industries=industries, search=search, selected_industry=industry)

@companies_bp.route("/add", methods=["GET", "POST"])
@role_required("admin", "placement_officer")
def add_company():
    if request.method == "POST":
        data = {
            "company_name": request.form.get("company_name"),
            "industry": request.form.get("industry"),
            "location": request.form.get("location"),
            "website": request.form.get("website"),
            "tier": request.form.get("tier")
        }
        success, result = create_company(data)
        if success:
            flash(f"Company '{data['company_name']}' registered successfully!", "success")
            return redirect(url_for("companies.list_companies"))
        else:
            flash(result, "danger")

    return render_template("companies/form.html", company=None, action="Add")

@companies_bp.route("/<int:company_id>")
@login_required
def view_company(company_id):
    company = get_company_by_id(company_id)
    if not company:
        flash("Company not found.", "warning")
        return redirect(url_for("companies.list_companies"))
    return render_template("companies/view.html", company=company)

@companies_bp.route("/<int:company_id>/edit", methods=["GET", "POST"])
@role_required("admin", "placement_officer")
def edit_company(company_id):
    company = get_company_by_id(company_id)
    if not company:
        flash("Company not found.", "warning")
        return redirect(url_for("companies.list_companies"))

    if request.method == "POST":
        data = {
            "company_name": request.form.get("company_name"),
            "industry": request.form.get("industry"),
            "location": request.form.get("location"),
            "website": request.form.get("website"),
            "tier": request.form.get("tier")
        }
        success, result = update_company(company_id, data)
        if success:
            flash(f"Company '{data['company_name']}' updated successfully!", "success")
            return redirect(url_for("companies.view_company", company_id=company_id))
        else:
            flash(result, "danger")

    return render_template("companies/form.html", company=company, action="Edit")

@companies_bp.route("/<int:company_id>/delete", methods=["POST"])
@role_required("admin", "placement_officer")
def remove_company(company_id):
    company = get_company_by_id(company_id)
    if not company:
        flash("Company not found.", "warning")
        return redirect(url_for("companies.list_companies"))

    if delete_company(company_id):
        flash(f"Company '{company['company_name']}' removed.", "info")
    else:
        flash("Could not delete company.", "danger")
    return redirect(url_for("companies.list_companies"))
