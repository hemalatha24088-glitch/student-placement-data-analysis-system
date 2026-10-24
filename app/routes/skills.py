"""
Skills Management Blueprint.
Provides listing, creation, editing, and association breakdowns for skills.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app import csrf
from app.services.skill_service import (
    get_all_skills,
    get_skill_by_id,
    create_skill,
    update_skill,
    delete_skill,
    get_skill_categories
)
from app.services.skill_recommender_service import (
    analyze_skill_gap,
    analyze_student_skill_gap,
    TIER_PROFILES,
    get_target_skills_for_company
)
from app.services.student_service import get_all_students_simple, get_student_by_id
from app.services.company_service import get_companies
from app.utils.auth import login_required, role_required

skills_bp = Blueprint("skills", __name__, url_prefix="/skills")

@skills_bp.route("/")
@login_required
def list_skills():
    category = request.args.get("category", "All")
    skills = get_all_skills(category=category)
    categories = get_skill_categories()
    return render_template("skills/index.html", skills=skills, categories=categories, selected_category=category)

@skills_bp.route("/add", methods=["POST"])
@role_required("admin", "placement_officer")
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
@role_required("admin", "placement_officer")
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
@role_required("admin", "placement_officer")
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

@skills_bp.route("/recommender", methods=["GET", "POST"])
@login_required
def recommender():
    """
    Smart Skill Gap & Preparation Roadmap Recommender.
    Evaluates candidate skills against recruiter tier or company expectations,
    identifying exact missing proficiencies and generating 6-week roadmaps.
    """
    students = get_all_students_simple()
    companies = get_companies()
    all_skills = get_all_skills()

    target_type = request.values.get("target_type", "tier")
    target_value = request.values.get("target_value", "Super Dream")
    student_id_val = request.values.get("student_id")

    analysis = None
    selected_student_id = None
    custom_skills = []

    # If student is selected
    if student_id_val:
        try:
            selected_student_id = int(student_id_val)
            analysis = analyze_student_skill_gap(selected_student_id, target_type=target_type, target_value=target_value)
            if analysis and analysis.get("student"):
                custom_skills = [s["skill_name"] for s in analysis["student"].get("skills", [])]
        except (ValueError, TypeError):
            selected_student_id = None

    # If manual custom skills submitted via POST
    if request.method == "POST" and not selected_student_id:
        custom_skills = request.form.getlist("skills")
        analysis = analyze_skill_gap(custom_skills, target_type=target_type, target_value=target_value)

    # Fallback to default student if no analysis yet
    if not analysis and students:
        # Pick the first unplaced or first available student
        fallback_student = next((s for s in students if s.get("placement_status") == "Unplaced"), students[0])
        selected_student_id = fallback_student["student_id"]
        analysis = analyze_student_skill_gap(selected_student_id, target_type=target_type, target_value=target_value)
        if analysis and analysis.get("student"):
            custom_skills = [s["skill_name"] for s in analysis["student"].get("skills", [])]

    # Target company name resolution
    target_company = None
    if target_type == "company":
        try:
            cid = int(target_value)
            target_company = next((c for c in companies if c["company_id"] == cid), None)
        except (ValueError, TypeError):
            pass

    return render_template(
        "skills/recommender.html",
        students=students,
        companies=companies,
        tier_profiles=TIER_PROFILES,
        analysis=analysis,
        selected_student_id=selected_student_id,
        target_type=target_type,
        target_value=target_value,
        target_company=target_company,
        all_skills=all_skills,
        custom_skills=custom_skills
    )

@skills_bp.route("/api/recommender", methods=["POST"])
@csrf.exempt
def api_recommender():
    """JSON API endpoint for real-time skill gap analysis."""
    data = request.get_json() or {}
    target_type = data.get("target_type", "tier")
    target_value = data.get("target_value", "Super Dream")
    student_id = data.get("student_id")
    skills = data.get("skills", [])

    if student_id:
        try:
            analysis = analyze_student_skill_gap(int(student_id), target_type=target_type, target_value=target_value)
            return jsonify({"success": True, "analysis": analysis})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 400
    else:
        analysis = analyze_skill_gap(skills, target_type=target_type, target_value=target_value)
        return jsonify({"success": True, "analysis": analysis})

