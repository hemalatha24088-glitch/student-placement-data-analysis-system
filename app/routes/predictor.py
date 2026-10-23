"""
Placement Probability Predictor Blueprint.
Provides interactive Machine Learning classification, what-if candidate evaluation,
feature importance diagnostics, and unplaced student risk prioritization.
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from app.services.ml_service import predictor_service, salary_predictor_service
from app.services.student_service import get_all_departments, get_all_graduation_years, get_all_students_simple
from app.services.skill_service import get_all_skills

predictor_bp = Blueprint("predictor", __name__, url_prefix="/predictor")

@predictor_bp.route("/", methods=["GET", "POST"])
def index():
    departments = get_all_departments()
    years = get_all_graduation_years()
    all_skills = get_all_skills()

    prediction_result = None
    default_cgpa = 8.0
    default_dept = departments[0] if departments else "Computer Science and Engineering"
    default_year = 2026
    default_skills = ["Python", "SQL", "Data Structures & Algorithms"]

    if request.method == "POST":
        cgpa_str = request.form.get("cgpa", "8.0")
        try:
            cgpa = float(cgpa_str)
        except ValueError:
            cgpa = 7.5

        dept = request.form.get("department", default_dept)
        year_str = request.form.get("graduation_year", "2026")
        try:
            year = int(year_str)
        except ValueError:
            year = 2026

        eligible = 1 if request.form.get("eligible", "1") in ("1", "on", "true") else 0
        selected_skills = request.form.getlist("skills")

        prediction_result = predictor_service.predict_custom(
            cgpa=cgpa,
            department=dept,
            skills_list=selected_skills,
            graduation_year=year,
            eligible=eligible
        )
        default_cgpa = cgpa
        default_dept = dept
        default_year = year
        default_skills = selected_skills
    else:
        # Default initial prediction for display
        prediction_result = predictor_service.predict_custom(
            cgpa=default_cgpa,
            department=default_dept,
            skills_list=default_skills,
            graduation_year=default_year,
            eligible=1
        )

    # Risk ranking of current unplaced candidates
    unplaced_cohort = predictor_service.get_unplaced_risk_cohort()

    return render_template(
        "predictor/index.html",
        prediction=prediction_result,
        unplaced_cohort=unplaced_cohort,
        departments=departments,
        years=years,
        all_skills=all_skills,
        model_metrics=predictor_service.metrics,
        feature_importances=predictor_service.feature_importances[:8],
        form_cgpa=default_cgpa,
        form_dept=default_dept,
        form_year=default_year,
        form_skills=default_skills
    )

@predictor_bp.route("/api/predict", methods=["POST"])
def api_predict():
    """JSON API endpoint for real-time slider/input reactivity."""
    data = request.get_json() or {}
    cgpa = float(data.get("cgpa", 7.5))
    dept = data.get("department", "Computer Science and Engineering")
    skills = data.get("skills", [])
    year = int(data.get("graduation_year", 2026))
    eligible = int(data.get("eligible", 1))

    res = predictor_service.predict_custom(
        cgpa=cgpa,
        department=dept,
        skills_list=skills,
        graduation_year=year,
        eligible=eligible
    )
    return jsonify({"success": True, "prediction": res})

@predictor_bp.route("/retrain", methods=["POST"])
def retrain_model():
    """Retrain the model on updated MySQL records."""
    success, msg = predictor_service.train()
    if success:
        flash("Random Forest Placement Predictor successfully retrained on current database records!", "success")
    else:
        flash(f"Model retraining failed: {msg}", "danger")
    return redirect(url_for("predictor.index"))

@predictor_bp.route("/salary", methods=["GET", "POST"])
def salary_predictor():
    """
    Salary Package (CTC) Predictor Blueprint.
    Uses Machine Learning Regression to estimate annual compensation package in LPA,
    salary confidence bands, tier classification, and skill value drivers.
    """
    departments = get_all_departments()
    all_skills = get_all_skills()
    students = get_all_students_simple()

    default_cgpa = 8.0
    default_dept = departments[0] if departments else "Computer Science and Engineering"
    default_skills = ["Python", "SQL", "Data Structures & Algorithms"]
    selected_student_id = request.values.get("student_id")

    prediction_result = None
    if selected_student_id:
        try:
            sid = int(selected_student_id)
            pred = salary_predictor_service.predict_student(sid)
            if pred and pred.get("student"):
                default_cgpa = float(pred["student"].get("cgpa") or 8.0)
                default_dept = pred["student"].get("department", default_dept)
                default_skills = [s["skill_name"] for s in pred["student"].get("skills", [])]
                prediction_result = pred
            else:
                prediction_result = salary_predictor_service.predict_custom(default_cgpa, default_dept, default_skills)
        except (ValueError, TypeError):
            prediction_result = salary_predictor_service.predict_custom(default_cgpa, default_dept, default_skills)
    elif request.method == "POST":
        try:
            cgpa = float(request.form.get("cgpa", default_cgpa))
        except (ValueError, TypeError):
            cgpa = 8.0
        dept = request.form.get("department", default_dept)
        selected_skills = request.form.getlist("skills")
        prediction_result = salary_predictor_service.predict_custom(cgpa, dept, selected_skills)
        default_cgpa = cgpa
        default_dept = dept
        default_skills = selected_skills
    else:
        prediction_result = salary_predictor_service.predict_custom(default_cgpa, default_dept, default_skills)

    return render_template(
        "predictor/salary.html",
        prediction=prediction_result,
        departments=departments,
        all_skills=all_skills,
        students=students,
        selected_student_id=selected_student_id,
        form_cgpa=default_cgpa,
        form_dept=default_dept,
        form_skills=default_skills,
        model_metrics=salary_predictor_service.metrics,
        feature_importances=salary_predictor_service.feature_importances[:8]
    )

@predictor_bp.route("/api/predict-salary", methods=["POST"])
def api_predict_salary():
    """JSON API endpoint for real-time CTC prediction reactivity."""
    data = request.get_json() or {}
    try:
        cgpa = float(data.get("cgpa", 8.0))
    except (ValueError, TypeError):
        cgpa = 8.0
    dept = data.get("department", "Computer Science and Engineering")
    skills = data.get("skills", [])
    res = salary_predictor_service.predict_custom(cgpa, dept, skills)
    return jsonify({"success": True, "prediction": res})

@predictor_bp.route("/salary/retrain", methods=["POST"])
def retrain_salary_model():
    """Retrain Random Forest CTC Regressor on updated MySQL records."""
    success, msg = salary_predictor_service.train()
    if success:
        flash("Random Forest Salary Package Regressor successfully retrained on current database records!", "success")
    else:
        flash(f"Model retraining failed: {msg}", "danger")
    return redirect(url_for("predictor.salary_predictor"))

