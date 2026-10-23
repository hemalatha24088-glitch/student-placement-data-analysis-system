"""
Skills Management Blueprint.
Provides listing, creation, editing, and association breakdowns for skills.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.services.skill_service import (
    get_all_skills,
    get_skill_by_id,
    create_skill,
    update_skill,
    delete_skill,
    get_skill_categories
)

skills_bp = Blueprint("skills", __name__, url_prefix="/skills")

@skills_bp.route("/")
def list_skills():
    category = request.args.get("category", "All")
    skills = get_all_skills(category=category)
    categories = get_skill_categories()
    return render_template("skills/index.html", skills=skills, categories=categories, selected_category=category)

@skills_bp.route("/add", methods=["POST"])
def add_skill():
    name = request.form.get("skill_name", "")
    category = request.form.get("skill_category", "Technical")
    success, result = create_skill(name, category)
    if success:
        flash(f"Skill '{name.strip()}' added successfully!", "success")
    else:
        flash(result, "danger")
    return redirect(url_for("skills.list_skills"))

@skills_bp.route("/<int:skill_id>/edit", methods=["POST"])
def edit_skill(skill_id):
    name = request.form.get("skill_name", "")
    category = request.form.get("skill_category", "Technical")
    success, result = update_skill(skill_id, name, category)
    if success:
        flash("Skill updated successfully!", "success")
    else:
        flash(result, "danger")
    return redirect(url_for("skills.list_skills"))

@skills_bp.route("/<int:skill_id>/delete", methods=["POST"])
def remove_skill(skill_id):
    skill = get_skill_by_id(skill_id)
    if not skill:
        flash("Skill not found.", "warning")
        return redirect(url_for("skills.list_skills"))

    if delete_skill(skill_id):
        flash(f"Skill '{skill['skill_name']}' deleted.", "info")
    else:
        flash("Could not delete skill.", "danger")
    return redirect(url_for("skills.list_skills"))
