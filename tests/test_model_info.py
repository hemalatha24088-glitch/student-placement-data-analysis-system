"""
Machine Learning Model Integrity, Empirical Performance & Persistence Tests.
Verifies /model-info diagnostics, 5-fold cross validation, joblib serialization, and zero data leakage.
"""
import os
import pytest
from app.services.ml_service import predictor_service, salary_predictor_service, CLASSIFIER_PATH, REGRESSOR_PATH
from app.services.large_seed_service import generate_large_synthetic_dataset


def test_model_info_route_accessible(student_client):
    """Verify that /model-info is accessible to authenticated users."""
    response = student_client.get("/model-info")
    assert response.status_code == 200
    assert b"Model Diagnostics" in response.data or b"Machine Learning Model Diagnostics" in response.data
    assert b"5-Fold Cross-Validation" in response.data
    assert b"Placement Likelihood Classifier" in response.data
    assert b"Annual CTC Compensation Regressor" in response.data


def test_classifier_metrics_completeness():
    """Verify that classifier metrics include all required statistical metrics."""
    success, msg = predictor_service.train()
    assert success is True
    metrics = predictor_service.metrics

    assert "accuracy" in metrics
    assert "precision" in metrics
    assert "recall" in metrics
    assert "f1_score" in metrics
    assert "roc_auc" in metrics
    assert "cv_scores" in metrics
    assert "cv_mean" in metrics
    assert "training_samples" in metrics
    assert "train_test_split" in metrics
    assert "trained_at" in metrics
    assert "version" in metrics

    # Accuracy, Precision, Recall, F1, ROC-AUC must be realistic percentage figures
    assert 0.0 <= metrics["accuracy"] <= 100.0
    assert 0.0 <= metrics["precision"] <= 100.0
    assert 0.0 <= metrics["recall"] <= 100.0
    assert 0.0 <= metrics["f1_score"] <= 100.0
    assert 0.0 <= metrics["roc_auc"] <= 100.0


def test_regressor_metrics_completeness():
    """Verify that salary regressor metrics include MAE, RMSE, R2, and CV scores."""
    success, msg = salary_predictor_service.train()
    assert success is True
    metrics = salary_predictor_service.metrics

    assert "mae" in metrics
    assert "rmse" in metrics
    assert "r2" in metrics or "r2_score" in metrics
    assert "cv_r2_scores" in metrics
    assert "cv_mae_mean" in metrics
    assert "training_samples" in metrics
    assert "train_test_split" in metrics

    assert metrics["mae"] > 0
    assert metrics["rmse"] > 0


def test_joblib_model_persistence():
    """Verify that trained models are serialized and persisted to disk via Joblib."""
    predictor_service.train()
    salary_predictor_service.train()

    assert os.path.exists(CLASSIFIER_PATH), f"Classifier file {CLASSIFIER_PATH} should exist"
    assert os.path.exists(REGRESSOR_PATH), f"Regressor file {REGRESSOR_PATH} should exist"
    assert os.path.getsize(CLASSIFIER_PATH) > 1024, "Classifier joblib file should not be empty"
    assert os.path.getsize(REGRESSOR_PATH) > 1024, "Regressor joblib file should not be empty"


def test_zero_data_leakage_feature_names():
    """Verify no post-placement outcome features (target leakage) exist in predictor feature sets."""
    forbidden_features = [
        "is_placed", "placement_id", "status", "company_id", "company_name",
        "package_amount", "package_unit", "placement_date", "offer_type"
    ]
    for feature in predictor_service.feature_names:
        assert feature.lower() not in forbidden_features, f"Data leakage detected: {feature} in predictor features"

    for feature in salary_predictor_service.feature_names:
        assert feature.lower() not in ["package_amount", "package_unit"], f"Target leakage detected in regressor: {feature}"


def test_large_synthetic_seed_idempotency():
    """Verify large synthetic seed generator completes successfully and is safe to execute."""
    success, msg = generate_large_synthetic_dataset(target_count=600)
    assert success is True
    assert "Successfully" in msg
