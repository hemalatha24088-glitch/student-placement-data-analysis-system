"""
Student Management Blueprint.
Provides full CRUD: List, Add, View, Edit, Delete, and Skill Association.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort, session
from app.services.student_service import (
    get_students,
    get_student_by_id,
    create_student,
    update_student,
    delete_student,
    get_all_departments,
    get_all_graduation_years
)
from app.services.skill_service import get_all_skills
from app.utils.auth import login_required, role_required

students_bp = Blueprint("students", __name__, url_prefix="/students")

@students_bp.route("/")
@role_required("admin", "placement_officer")
def list_students():
    page = request.args.get("page", 1, type=int)
    dept = request.args.get("department", "All")
    year = request.args.get("graduation_year", "All")
    eligibility = request.args.get("eligibility", "All")
    search = request.args.get("search", "").strip()
    sort_by = request.args.get("sort_by", "roll_no")

    result = get_students(
        department=dept,
        graduation_year=year,
        eligibility=eligibility,
        search=search,
        page=page,
        per_page=12,
        sort_by=sort_by
    )

    departments = get_all_departments()
    graduation_years = get_all_graduation_years()

    return render_template(
        "students/index.html",
        students=result["students"],
        total=result["total"],
        page=result["page"],
        per_page=result["per_page"],
        total_pages=result["total_pages"],
        departments=departments,
        graduation_years=graduation_years,
        selected_dept=dept,
        selected_year=year,
        selected_eligibility=eligibility,
        search=search,
        sort_by=sort_by
    )

@students_bp.route("/add", methods=["GET", "POST"])
@role_required("admin", "placement_officer")
def add_student():
    if request.method == "POST":
        data = {
            "roll_no": request.form.get("roll_no"),
            "student_name": request.form.get("student_name"),
            "department": request.form.get("department"),
            "graduation_year": request.form.get("graduation_year"),
            "cgpa": request.form.get("cgpa") or None,
            "email": request.form.get("email"),
            "phone": request.form.get("phone"),
            "gender": request.form.get("gender"),
            "eligible_for_placement": request.form.get("eligible_for_placement")
        }
        selected_skills = request.form.getlist("skills")

        success, result = create_student(data, skill_ids=selected_skills)
        if success:
            flash(f"Student '{data['student_name']}' ({data['roll_no']}) registered successfully!", "success")
            return redirect(url_for("students.view_student", student_id=result))
        else:
            flash(result, "danger")

    departments = get_all_departments()
    all_skills = get_all_skills()
    return render_template("students/form.html", student=None, departments=departments, all_skills=all_skills, action="Add")

@students_bp.route("/<int:student_id>")
@login_required
def view_student(student_id):
    user_role = session.get("role", "student")
    student = get_student_by_id(student_id)
    if not student:
        flash("Student record not found.", "warning")
        return redirect(url_for("main.dashboard"))

    if user_role == "student":
        user_student_id = session.get("student_id")
        is_own_profile = (user_student_id and int(user_student_id) == int(student_id)) or \
                         (student.get("email") and student.get("email") == session.get("email")) or \
                         (student.get("roll_no") and student.get("roll_no") == session.get("username"))
        if not is_own_profile:
            abort(403)
    
    from app.services.ml_service import predictor_service, salary_predictor_service
    from app.services.skill_recommender_service import analyze_student_skill_gap
    prediction = predictor_service.predict_student(student_id)
    salary_pred = salary_predictor_service.predict_student(student_id)
    dream_gap = analyze_student_skill_gap(student_id, target_type="tier", target_value="Dream")
    super_dream_gap = analyze_student_skill_gap(student_id, target_type="tier", target_value="Super Dream")
    return render_template(
        "students/view.html",
        student=student,
        prediction=prediction,
        salary_pred=salary_pred,
        dream_gap=dream_gap,
        super_dream_gap=super_dream_gap
    )

@students_bp.route("/<int:student_id>/resume")
@login_required
def student_resume(student_id):
    """
    Automated Student Placement Bio-Data & Verified Credential Document.
    Print-ready and PDF-exportable for campus recruitment drives.
    """
    user_role = session.get("role", "student")
    student = get_student_by_id(student_id)
    if not student:
        flash("Student record not found.", "warning")
        return redirect(url_for("main.dashboard"))

    if user_role == "student":
        user_student_id = session.get("student_id")
        is_own_profile = (user_student_id and int(user_student_id) == int(student_id)) or \
                         (student.get("email") and student.get("email") == session.get("email")) or \
                         (student.get("roll_no") and student.get("roll_no") == session.get("username"))
        if not is_own_profile:
            abort(403)

    from app.services.ml_service import predictor_service, salary_predictor_service
    prediction = predictor_service.predict_student(student_id)
    salary_pred = salary_predictor_service.predict_student(student_id)

    return render_template(
        "students/resume.html",
        student=student,
        prediction=prediction,
        salary_pred=salary_pred
    )

@students_bp.route("/<int:student_id>/edit", methods=["GET", "POST"])
@role_required("admin", "placement_officer")
def edit_student(student_id):
    student = get_student_by_id(student_id)
    if not student:
        flash("Student record not found.", "warning")
        return redirect(url_for("students.list_students"))

    if request.method == "POST":
        data = {
            "roll_no": request.form.get("roll_no"),
            "student_name": request.form.get("student_name"),
            "department": request.form.get("department"),
            "graduation_year": request.form.get("graduation_year"),
            "cgpa": request.form.get("cgpa") or None,
            "email": request.form.get("email"),
            "phone": request.form.get("phone"),
            "gender": request.form.get("gender"),
            "eligible_for_placement": request.form.get("eligible_for_placement")
        }
        selected_skills = request.form.getlist("skills")

        success, result = update_student(student_id, data, skill_ids=selected_skills)
        if success:
            flash(f"Student '{data['student_name']}' updated successfully!", "success")
            return redirect(url_for("students.view_student", student_id=student_id))
        else:
            flash(result, "danger")

    departments = get_all_departments()
    all_skills = get_all_skills()
    student_skill_ids = [s["skill_id"] for s in student.get("skills", [])]

    return render_template(
        "students/form.html",
        student=student,
        departments=departments,
        all_skills=all_skills,
        student_skill_ids=student_skill_ids,
        action="Edit"
    )

@students_bp.route("/<int:student_id>/delete", methods=["POST"])
@role_required("admin", "placement_officer")
def remove_student(student_id):
    student = get_student_by_id(student_id)
    if not student:
        flash("Student not found.", "warning")
        return redirect(url_for("students.list_students"))

    if delete_student(student_id):
        flash(f"Student record for {student['student_name']} ({student['roll_no']}) deleted.", "info")
    else:
        flash("Could not delete student record.", "danger")
    return redirect(url_for("students.list_students"))
