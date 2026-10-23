"""
Unit tests for Natural Language Processing (NLP) ATS Resume & Job Description Matcher.
"""
import pytest
from app import create_app
from app.services.nlp_service import (
    clean_text,
    extract_keywords,
    calculate_ats_match,
    generate_student_resume_text,
    SAMPLE_JOB_DESCRIPTIONS
)

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_clean_text_normalization():
    """Verify text cleaning removes punctuation and normalizes whitespace."""
    raw = "  Python & Machine-Learning!  (SQL/NoSQL)   "
    cleaned = clean_text(raw)
    assert "python" in cleaned
    assert "machine learning" in cleaned
    assert "!" not in cleaned

def test_keyword_extraction():
    """Verify domain keyword extraction against ontology."""
    sample = "Software engineer skilled in Python, SQL, React.js, Docker, and Data Structures."
    kws = extract_keywords(sample)
    assert "python" in kws
    assert "sql" in kws
    assert "docker" in kws
    assert "data structures" in kws

def test_calculate_ats_match():
    """Verify TF-IDF and keyword matching between resume and job description."""
    resume = "Passionate Python developer with solid Data Structures & Algorithms, Machine Learning, SQL, and Git."
    jd = SAMPLE_JOB_DESCRIPTIONS["google_swe"]["text"]

    result = calculate_ats_match(resume, jd)
    assert 0.0 <= result["ats_score"] <= 100.0
    assert result["ats_score"] > 15.0
    assert len(result["matched_keywords"]) > 0
    assert isinstance(result["missing_keywords"], list)
    assert "recommendations" in result
    assert len(result["recommendations"]) > 0

def test_empty_ats_match():
    """Verify handling of empty inputs."""
    res = calculate_ats_match("", "")
    assert res["ats_score"] == 0.0
    assert "Input Required" in res["readiness"]

def test_generate_student_resume_text():
    """Verify dynamic resume generation for registered student."""
    resume_text = generate_student_resume_text(1)
    assert len(resume_text) > 50
    assert "Candidate Name:" in resume_text
    assert "TECHNICAL COMPETENCIES" in resume_text

def test_ats_routes(client):
    """Verify GET and POST requests to the /ats UI and API routes."""
    get_resp = client.get("/ats")
    assert get_resp.status_code == 200
    assert b"ATS Compatibility" in get_resp.data

    post_resp = client.post("/ats", data={
        "resume_text": "Experienced Python and SQL developer with Machine Learning capstones.",
        "jd_text": SAMPLE_JOB_DESCRIPTIONS["google_swe"]["text"]
    })
    assert post_resp.status_code == 200
    assert b"ATS Score" in post_resp.data

    # Test API endpoints
    api_resp = client.post("/ats/api/match", json={
        "resume_text": "Python, SQL, DSA engineer",
        "jd_text": "Looking for Python, SQL, DSA developer"
    })
    assert api_resp.status_code == 200
    assert api_resp.get_json()["success"] is True

    jd_resp = client.get("/ats/api/sample-jd/google_swe")
    assert jd_resp.status_code == 200
    assert jd_resp.get_json()["success"] is True

    st_resp = client.get("/ats/api/student-resume/1")
    assert st_resp.status_code == 200
    assert st_resp.get_json()["success"] is True
