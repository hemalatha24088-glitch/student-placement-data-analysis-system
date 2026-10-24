"""
Role-Based Access Control (RBAC) Security Verification Test Suite.
Validates least-privilege matrix across Anonymous, Student, Placement Officer, and Admin.
"""
import pytest


def test_anonymous_redirected_to_login(client):
    """Anonymous visitors to protected routes must be redirected (302) to login."""
    protected_urls = [
        "/dashboard",
        "/students/",
        "/students/add",
        "/companies/add",
        "/placements/",
        "/import/",
        "/reports/",
        "/admin/users",
        "/auth/change-password"
    ]
    for url in protected_urls:
        resp = client.get(url, follow_redirects=False)
        assert resp.status_code == 302, f"Expected 302 redirect for {url}, got {resp.status_code}"
        assert "/login" in resp.headers["Location"], f"Expected redirect to /login for {url}"


def test_student_role_access_boundaries(student_client):
    """Students can access self profile, predictor, and recommender, but are blocked from staff routes."""
    # Permitted endpoints
    allowed_urls = [
        "/predictor/",
        "/predictor/salary",
        "/skills/recommender",
        "/ats/"
    ]
    for url in allowed_urls:
        resp = student_client.get(url)
        assert resp.status_code == 200, f"Expected 200 OK for student on {url}, got {resp.status_code}"

    # Forbidden endpoints (Must return 403 Forbidden)
    forbidden_urls = [
        "/students/add",
        "/companies/add",
        "/placements/add",
        "/import/",
        "/reports/",
        "/admin/users"
    ]
    for url in forbidden_urls:
        resp = student_client.get(url)
        assert resp.status_code == 403, f"Expected 403 Forbidden for student on {url}, got {resp.status_code}"


def test_student_cannot_view_or_edit_other_student_profile(student_client):
    """Student with student_id=1 cannot access student_id=2 (IDOR protection)."""
    resp = student_client.get("/students/2")
    assert resp.status_code == 403


def test_placement_officer_access_boundaries(officer_client):
    """Officers can manage students, companies, placements, imports, and reports, but NOT admin user management."""
    officer_allowed_urls = [
        "/dashboard",
        "/students/",
        "/students/add",
        "/companies/",
        "/companies/add",
        "/placements/",
        "/placements/add",
        "/import/",
        "/reports/",
        "/predictor/",
        "/skills/recommender"
    ]
    for url in officer_allowed_urls:
        resp = officer_client.get(url)
        assert resp.status_code == 200, f"Expected 200 OK for officer on {url}, got {resp.status_code}"

    # Officer must be blocked from Administrator User Management
    resp = officer_client.get("/admin/users")
    assert resp.status_code == 403


def test_administrator_full_access(admin_client):
    """Administrators have access across all management portals including User Management."""
    admin_urls = [
        "/dashboard",
        "/students/",
        "/companies/",
        "/placements/",
        "/import/",
        "/reports/",
        "/admin/users"
    ]
    for url in admin_urls:
        resp = admin_client.get(url)
        assert resp.status_code == 200, f"Expected 200 OK for admin on {url}, got {resp.status_code}"
