"""
Unit tests for Machine Learning Placement Predictor service.
"""

import pytest

from app.services.ml_service import predictor_service


def test_model_training_and_metrics():
    """Verify that Random Forest model trains and produces evaluation metrics."""
    success, msg = predictor_service.train()
    assert success is True
    assert "successfully trained" in msg
    assert predictor_service.model is not None
    assert predictor_service.metrics["algorithm"] == "Random Forest Classifier (Ensemble)"
    assert predictor_service.metrics["training_samples"] > 0
    assert predictor_service.metrics["accuracy"] >= 70.0
    assert len(predictor_service.feature_importances) > 0


def test_custom_prediction():
    """Verify inference for a high-performing student candidate."""
    pred = predictor_service.predict_custom(
        cgpa=9.2,
        department="Computer Science and Engineering",
        skills_list=["Python", "Data Structures & Algorithms", "SQL"],
        graduation_year=2026,
        eligible=1,
    )
    assert 0.0 <= pred["probability_pct"] <= 100.0
    assert pred["probability_pct"] >= 70.0
    assert "High Probability" in pred["risk_tier"]
    assert len(pred["strengths"]) > 0


def test_ineligible_student_penalization():
    """Verify that candidate marked ineligible receives low placement probability."""
    pred = predictor_service.predict_custom(
        cgpa=5.2, department="Mechanical Engineering", skills_list=[], graduation_year=2026, eligible=0
    )
    assert pred["probability_pct"] <= 20.0
    assert "At Risk" in pred["risk_tier"]
    assert len(pred["recommendations"]) > 0


def test_unplaced_risk_cohort():
    """Verify unplaced students cohort ranking."""
    cohort = predictor_service.get_unplaced_risk_cohort()
    assert isinstance(cohort, list)
    for c in cohort:
        assert "roll_no" in c
        assert "probability_pct" in c
        assert 0.0 <= c["probability_pct"] <= 100.0


def test_predictor_routes_and_api(student_client, officer_client):
    """Verify Predictor UI routes, POST form inference, JSON API, and retraining."""
    # 1. GET /predictor/
    get_resp = student_client.get("/predictor/")
    assert get_resp.status_code == 200
    assert b"Placement Probability" in get_resp.data

    # 2. POST /predictor/ form inference
    post_resp = student_client.post(
        "/predictor/",
        data={
            "cgpa": "9.5",
            "department": "Computer Science and Engineering",
            "graduation_year": "2026",
            "eligible": "1",
            "skills": ["Python", "SQL"],
        },
    )
    assert post_resp.status_code == 200
    assert b"Placement Probability" in post_resp.data

    # 3. POST /predictor/api/predict JSON API
    api_resp = student_client.post(
        "/predictor/api/predict",
        json={
            "cgpa": 8.5,
            "department": "Computer Science and Engineering",
            "graduation_year": 2026,
            "eligible": 1,
            "skills": ["Python", "Machine Learning"],
        },
    )
    assert api_resp.status_code == 200
    api_data = api_resp.get_json()
    assert api_data["success"] is True
    assert "prediction" in api_data

    # 4. POST /predictor/retrain (Officer required)
    retrain_resp = officer_client.post("/predictor/retrain", follow_redirects=True)
    assert retrain_resp.status_code == 200
    assert b"retrained and persisted" in retrain_resp.data
