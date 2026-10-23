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
        eligible=1
    )
    assert 0.0 <= pred["probability_pct"] <= 100.0
    assert pred["probability_pct"] >= 70.0
    assert "High Probability" in pred["risk_tier"]
    assert len(pred["strengths"]) > 0

def test_ineligible_student_penalization():
    """Verify that candidate marked ineligible receives low placement probability."""
    pred = predictor_service.predict_custom(
        cgpa=5.2,
        department="Mechanical Engineering",
        skills_list=[],
        graduation_year=2026,
        eligible=0
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
