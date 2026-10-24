"""
Cross-Site Request Forgery (CSRF) Security Verification Test Suite.
Validates that untokened state-modifying requests are rejected with HTTP 400 Bad Request.
"""

import pytest


def test_csrf_protection_rejects_untokened_post(csrf_client):
    """POST request without CSRF token must fail with 400 Bad Request."""
    response = csrf_client.post("/login", data={"username": "admin", "password": "wrongpassword"})
    assert response.status_code == 400


def test_csrf_protection_rejects_untokened_registration(csrf_client):
    """Registration POST request without CSRF token must fail with 400."""
    response = csrf_client.post(
        "/register", data={"username": "attacker", "password": "Password123!", "confirm_password": "Password123!"}
    )
    assert response.status_code == 400


def test_csrf_allows_safe_get_requests(csrf_client):
    """GET requests are idempotent and must succeed without CSRF tokens."""
    response = csrf_client.get("/login")
    assert response.status_code == 200


def test_exempt_json_api_endpoints_accept_json_post(csrf_client):
    """JSON API endpoints marked with @csrf.exempt process API requests."""
    payload = {"cgpa": 8.5, "department": "Computer Science and Engineering", "skills": ["Python", "SQL"]}
    response = csrf_client.post("/predictor/api/predict-salary", json=payload)
    assert response.status_code == 200
