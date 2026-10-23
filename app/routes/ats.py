"""
Natural Language Processing (NLP) ATS Matcher Blueprint.
Provides interactive ATS resume screening, job description compatibility scoring,
keyword extraction, and keyword gap analysis.
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from app.services.nlp_service import (
    calculate_ats_match,
    generate_student_resume_text,
    SAMPLE_JOB_DESCRIPTIONS
)
from app.services.student_service import get_all_students_simple

ats_bp = Blueprint("ats", __name__, url_prefix="/ats")

@ats_bp.route("/", methods=["GET", "POST"], strict_slashes=False)
def index():
    students = get_all_students_simple()
    selected_student_id = request.values.get("student_id")
    selected_jd_key = request.values.get("jd_key", "google_swe")

    resume_text = request.values.get("resume_text", "")
    jd_text = request.values.get("jd_text", "")

    # If student is selected and no custom resume text provided, auto-generate
    if selected_student_id and not resume_text:
        try:
            resume_text = generate_student_resume_text(int(selected_student_id))
        except (ValueError, TypeError):
            pass

    # If default view and empty text, populate with default student and sample JD
    if not resume_text and students:
        resume_text = generate_student_resume_text(students[0]["student_id"])
        selected_student_id = students[0]["student_id"]

    if not jd_text:
        jd_text = SAMPLE_JOB_DESCRIPTIONS.get(selected_jd_key, {}).get("text", "")

    analysis = calculate_ats_match(resume_text, jd_text)

    return render_template(
        "ats/index.html",
        analysis=analysis,
        students=students,
        selected_student_id=selected_student_id,
        sample_jds=SAMPLE_JOB_DESCRIPTIONS,
        selected_jd_key=selected_jd_key,
        resume_text=resume_text,
        jd_text=jd_text
    )

@ats_bp.route("/api/match", methods=["POST"])
def api_match():
    """JSON API endpoint for real-time ATS match scoring."""
    data = request.get_json() or {}
    resume_text = data.get("resume_text", "")
    jd_text = data.get("jd_text", "")
    result = calculate_ats_match(resume_text, jd_text)
    return jsonify({"success": True, "analysis": result})

@ats_bp.route("/api/sample-jd/<jd_key>", methods=["GET"])
def api_sample_jd(jd_key):
    """Retrieve sample job description text."""
    jd = SAMPLE_JOB_DESCRIPTIONS.get(jd_key)
    if not jd:
        return jsonify({"success": False, "error": "Job description not found"}), 404
    return jsonify({"success": True, "jd": jd})

@ats_bp.route("/api/student-resume/<int:student_id>", methods=["GET"])
def api_student_resume(student_id):
    """Retrieve ATS-formatted resume text for a registered student."""
    text = generate_student_resume_text(student_id)
    if not text:
        return jsonify({"success": False, "error": "Student not found"}), 404
    return jsonify({"success": True, "resume_text": text})
