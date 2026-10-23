"""
Unit tests for Machine Learning Salary Package (CTC) Regressor & Placement Bio-Data service.
"""
import pytest
from app import create_app
from app.services.ml_service import salary_predictor_service

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_salary_regressor_training_and_metrics():
    """Verify that Random Forest Regressor trains properly on MySQL compensation data."""
    success, msg = salary_predictor_service.train()
    assert success is True
    assert "successfully trained" in msg
    assert salary_predictor_service.model is not None
    assert salary_predictor_service.metrics["algorithm"] == "Random Forest Regressor (Ensemble)"
    assert salary_predictor_service.metrics["training_samples"] >= 10
    assert salary_predictor_service.metrics["mae"] > 0
    assert salary_predictor_service.metrics["mean_package"] > 0
    assert len(salary_predictor_service.feature_importances) > 0

def test_salary_custom_prediction():
    """Verify CTC inference for candidate with strong skills and GPA."""
    pred = salary_predictor_service.predict_custom(
        cgpa=9.1,
        department="Computer Science and Engineering",
        skills_list=["Python", "SQL", "Data Structures & Algorithms", "Machine Learning"]
    )
    assert 3.5 <= pred["predicted_ctc"] <= 45.0
    assert pred["predicted_ctc"] >= 12.0
    assert pred["range_low"] <= pred["predicted_ctc"] <= pred["range_high"]
    assert "Dream" in pred["tier"]
    assert pred["cgpa_delta"] > 0
    assert isinstance(pred["uplift_opportunities"], list)

def test_salary_student_inference():
    """Verify inference for an existing student from MySQL."""
    pred = salary_predictor_service.predict_student(student_id=1)
    assert pred is not None
    assert "predicted_ctc" in pred
    assert "student" in pred
    assert pred["student"]["student_id"] == 1

def test_salary_predictor_routes(client):
    """Verify GET and POST requests to the /predictor/salary UI route."""
    response = client.get("/predictor/salary")
    assert response.status_code == 200
    assert b"Candidate Salary Package (CTC) Predictor" in response.data or b"Salary Package" in response.data

    post_resp = client.post("/predictor/salary", data={
        "cgpa": "8.5",
        "department": "Computer Science and Engineering",
        "skills": ["Python", "SQL"]
    })
    assert post_resp.status_code == 200
    assert b"Projected Compensation" in post_resp.data

def test_api_predict_salary(client):
    """Verify JSON API endpoint for real-time CTC prediction reactivity."""
    payload = {
        "cgpa": 8.75,
        "department": "Artificial Intelligence and Machine Learning",
        "skills": ["Python", "Machine Learning", "Data Structures & Algorithms"]
    }
    response = client.post("/predictor/api/predict-salary", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert "prediction" in data
    assert data["prediction"]["predicted_ctc"] > 0

def test_student_resume_route(client):
    """Verify printable placement bio-data / resume route."""
    response = client.get("/students/1/resume")
    assert response.status_code == 200
    assert b"Verified Candidate Bio-Data" in response.data or b"Placement Bio-Data" in response.data
