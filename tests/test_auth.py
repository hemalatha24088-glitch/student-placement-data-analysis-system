"""
Unit tests for Authentication, Session Protection, RBAC, Password Policy, and OAuth.
"""
import time
import pytest
from app import create_app
from config import Config
from app.utils.auth import is_strong_password


def test_login_page_renders_with_demo_mode(app, client):
    """Verify that login portal renders properly and displays demo buttons when DEMO_MODE is True."""
    app.config["DEMO_MODE"] = True
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Sign In" in response.data
    assert b"Faculty Officer" in response.data
    assert b"Administrator" in response.data


def test_login_page_hides_demo_buttons_when_demo_mode_disabled():
    """Verify that demo buttons are hidden when DEMO_MODE is False (Security Requirement)."""
    class SecureConfig(Config):
        TESTING = True
        DEMO_MODE = False
        SECRET_KEY = "test-secret"
        WTF_CSRF_ENABLED = False

    secure_app = create_app(SecureConfig)
    with secure_app.test_client() as c:
        response = c.get("/login")
        assert response.status_code == 200
        assert b"Faculty Officer" not in response.data
        assert b"Administrator" not in response.data


def test_demo_login_faculty_when_enabled(app, client):
    """Verify one-click faculty reviewer demo login when DEMO_MODE is True."""
    app.config["DEMO_MODE"] = True
    response = client.get("/demo-login/faculty", follow_redirects=False)
    assert response.status_code == 302
    assert "/dashboard" in response.headers["Location"]
    with client.session_transaction() as sess:
        assert sess.get("username") == "faculty"
        assert sess.get("role") == "placement_officer"


def test_demo_login_admin_when_enabled(app, client):
    """Verify one-click administrator demo login when DEMO_MODE is True."""
    app.config["DEMO_MODE"] = True
    response = client.get("/demo-login/admin", follow_redirects=False)
    assert response.status_code == 302
    assert "/dashboard" in response.headers["Location"]
    with client.session_transaction() as sess:
        assert sess.get("username") == "admin"
        assert sess.get("role") == "admin"


def test_demo_login_rejected_when_disabled():
    """Verify demo login is rejected with an error when DEMO_MODE is False."""
    class SecureConfig(Config):
        TESTING = True
        DEMO_MODE = False
        SECRET_KEY = "test-secret"
        WTF_CSRF_ENABLED = False

    secure_app = create_app(SecureConfig)
    with secure_app.test_client() as c:
        response = c.get("/demo-login/faculty", follow_redirects=False)
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]


def test_invalid_credential_login(client):
    """Verify that bad credentials are rejected with a generic security error message."""
    response = client.post("/login", data={
        "username": "nonexistent_user",
        "password": "wrongpassword"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Invalid credentials" in response.data or b"Invalid username or password" in response.data


def test_logout(app, client):
    """Verify logout clears active user session."""
    app.config["DEMO_MODE"] = True
    client.get("/demo-login/faculty")
    with client.session_transaction() as sess:
        assert sess.get("user_id") is not None

    logout_resp = client.get("/logout", follow_redirects=False)
    assert logout_resp.status_code == 302
    with client.session_transaction() as sess:
        assert sess.get("user_id") is None


def test_register_page_renders_without_role_dropdown(client):
    """Verify registration page renders without role selection (Student only)."""
    response = client.get("/register")
    assert response.status_code == 200
    assert b"Create Student Account" in response.data
    assert b"Username" in response.data
    assert b"Password" in response.data
    # Ensure there is no select dropdown for role
    assert b'name="role"' not in response.data


def test_user_registration_enforces_student_role(client):
    """Verify public registration always assigns 'student' role, even if form attempts to inject 'admin'."""
    unique_user = f"reg_stu_{int(time.time() * 1000) % 100000}"
    unique_email = f"{unique_user}@university.edu"
    test_pass = "SecurePass123!"

    reg_response = client.post("/register", data={
        "full_name": "New Candidate",
        "username": unique_user,
        "email": unique_email,
        "role": "admin",  # Malicious attempt to elevate role
        "password": test_pass,
        "confirm_password": test_pass
    }, follow_redirects=False)

    assert reg_response.status_code == 302
    with client.session_transaction() as sess:
        assert sess.get("username") == unique_user
        # Must be student regardless of input
        assert sess.get("role") == "student"


def test_user_registration_mismatched_passwords(client):
    """Verify rejection when passwords do not match."""
    response = client.post("/register", data={
        "full_name": "Mismatch Tester",
        "username": f"mismatch_{int(time.time())}",
        "password": "Password123!",
        "confirm_password": "DifferentPassword456!"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Passwords do not match" in response.data


def test_user_registration_duplicate_username(client):
    """Verify rejection when attempting to register an already taken username."""
    # First registration
    uname = f"dup_{int(time.time())}"
    client.post("/register", data={
        "full_name": "Original User",
        "username": uname,
        "email": f"{uname}@mail.com",
        "password": "Password123!",
        "confirm_password": "Password123!"
    })
    client.get("/logout")

    # Second registration with same username
    response = client.post("/register", data={
        "full_name": "Imposter User",
        "username": uname,
        "email": f"other_{uname}@mail.com",
        "password": "Password123!",
        "confirm_password": "Password123!"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"already taken" in response.data


def test_google_login_hidden_when_unconfigured(client):
    """Verify Google Login button is hidden when GOOGLE_CLIENT_ID is not configured."""
    response = client.get("/login")
    assert response.status_code == 200
    # Since GOOGLE_CLIENT_ID is unset in test env, Google OAuth button must be hidden
    assert b"Sign in with Google" not in response.data
    assert b"Login with Google Account" not in response.data


def test_google_oauth_route_handles_unconfigured(client):
    """Verify accessing /auth/google safely redirects when OAuth is unconfigured."""
    response = client.get("/auth/google", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_password_policy_validation():
    """Verify password strength validation rules."""
    valid, msg = is_strong_password("Short1!")
    assert valid is False
    assert "8 characters" in msg

    valid, msg = is_strong_password("alllowercase123!")
    assert valid is False
    assert "uppercase" in msg

    valid, msg = is_strong_password("ALLUPPERCASE123!")
    assert valid is False
    assert "lowercase" in msg

    valid, msg = is_strong_password("NoDigitsHere!ABC")
    assert valid is False
    assert "digit" in msg

    valid, msg = is_strong_password("ValidPassword123")
    assert valid is True
