"""
Unit & Integration Tests for Main Blueprint Routes:
Landing page redirect, Overview showcase, Health checks, and filtered Dashboard.
"""

import pytest


def test_root_redirect_anonymous(client):
    """Anonymous user accessing root '/' should be redirected to /login."""
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_root_redirect_authenticated(student_client):
    """Authenticated user accessing root '/' should be redirected to /dashboard."""
    resp = student_client.get("/", follow_redirects=False)
    assert resp.status_code == 302
    assert "/dashboard" in resp.headers["Location"]


def test_overview_page_authenticated(student_client):
    """Authenticated user can view system features overview presentation."""
    resp = student_client.get("/overview")
    assert resp.status_code == 200
    assert b"Student Placement Data Analysis System" in resp.data or b"Placement" in resp.data


def test_health_check_html(client):
    """Health check HTML page returns 200 and database connectivity status."""
    resp = client.get("/health")
    assert resp.status_code == 200
    assert b"System Health" in resp.data or b"Database" in resp.data


def test_health_check_json(client):
    """Health check JSON endpoint returns connectivity and latency metrics."""
    resp = client.get("/api/health")
    assert resp.status_code in (200, 503)
    data = resp.get_json()
    assert "connected" in data
    assert "status" in data


def test_dashboard_with_filters(officer_client):
    """Dashboard supports deep query parameter combinations."""
    resp = officer_client.get(
        "/dashboard?department=Computer+Science+and+Engineering&graduation_year=2026&status=Placed"
    )
    assert resp.status_code == 200
    assert b"Placement Rate" in resp.data or b"Dashboard" in resp.data
