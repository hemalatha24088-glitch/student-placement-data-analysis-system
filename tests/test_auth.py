"""
Unit tests for Authentication, Login Gateway, and Session Protection.
"""
import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_login_page_renders(client):
    """Verify that the login portal page renders properly with credentials and demo profiles."""
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Sign In" in response.data
    assert b"Faculty Officer" in response.data
    assert b"Administrator" in response.data

def test_demo_login_faculty(client):
    """Verify one-click faculty reviewer demo login."""
    response = client.get("/demo-login/faculty", follow_redirects=False)
    assert response.status_code == 302
    assert "/dashboard" in response.headers["Location"]
    with client.session_transaction() as sess:
        assert sess.get("username") == "faculty"
        assert sess.get("role") == "placement_officer"

def test_demo_login_admin(client):
    """Verify one-click administrator demo login."""
    response = client.get("/demo-login/admin", follow_redirects=False)
    assert response.status_code == 302
    assert "/dashboard" in response.headers["Location"]
    with client.session_transaction() as sess:
        assert sess.get("username") == "admin"
        assert sess.get("role") == "admin"

def test_valid_credential_login(client):
    """Verify standard credential authentication against MySQL hashed password."""
    response = client.post("/login", data={
        "username": "admin",
        "password": "admin123"
    }, follow_redirects=False)
    assert response.status_code == 302
    assert "/dashboard" in response.headers["Location"]

def test_invalid_credential_login(client):
    """Verify that bad credentials are rejected."""
    response = client.post("/login", data={
        "username": "admin",
        "password": "wrongpassword"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Invalid credentials" in response.data

def test_logout(client):
    """Verify logout clears active user session."""
    client.get("/demo-login/faculty")
    with client.session_transaction() as sess:
        assert sess.get("user_id") is not None

    logout_resp = client.get("/logout", follow_redirects=False)
    assert logout_resp.status_code == 302
    with client.session_transaction() as sess:
        assert sess.get("user_id") is None

def test_google_login(client):
    """Verify Login with Google SSO flow."""
    response = client.get("/google-login", follow_redirects=False)
    assert response.status_code == 302
    assert "/dashboard" in response.headers["Location"]
    with client.session_transaction() as sess:
        assert sess.get("username") == "google_faculty"
        assert sess.get("role") == "placement_officer"
        assert sess.get("auth_provider") == "Google"

