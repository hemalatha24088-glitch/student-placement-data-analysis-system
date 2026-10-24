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
    """Verify Login with Google SSO flow with default evaluator account."""
    response = client.get("/google-login", follow_redirects=False)
    assert response.status_code == 302
    assert "/dashboard" in response.headers["Location"]
    with client.session_transaction() as sess:
        assert sess.get("username") == "google_faculty"
        assert sess.get("role") == "placement_officer"
        assert sess.get("auth_provider") == "Google"

def test_register_page_renders(client):
    """Verify that the user registration (Sign-Up) page renders properly."""
    response = client.get("/register")
    assert response.status_code == 200
    assert b"Create Your Placement Account" in response.data
    assert b"Username" in response.data
    assert b"Password" in response.data

def test_user_registration_and_direct_login(client):
    """Verify first-time user registration followed by direct credential login."""
    import time
    test_user = f"testuser_{int(time.time())}"
    test_email = f"{test_user}@placement.edu"
    test_pass = "MySecretPass123"

    # Step 1: Register as a new user
    reg_response = client.post("/register", data={
        "full_name": "Test Placement Officer",
        "username": test_user,
        "email": test_email,
        "role": "placement_officer",
        "password": test_pass,
        "confirm_password": test_pass
    }, follow_redirects=False)

    assert reg_response.status_code == 302
    assert "/dashboard" in reg_response.headers["Location"]

    with client.session_transaction() as sess:
        assert sess.get("username") == test_user
        assert sess.get("full_name") == "Test Placement Officer"
        assert sess.get("role") == "placement_officer"

    # Step 2: Sign out
    client.get("/logout")

    # Step 3: Log in using newly created username directly
    login_user_resp = client.post("/login", data={
        "username": test_user,
        "password": test_pass
    }, follow_redirects=False)
    assert login_user_resp.status_code == 302
    assert "/dashboard" in login_user_resp.headers["Location"]

    # Step 4: Sign out again
    client.get("/logout")

    # Step 5: Log in using newly created email directly
    login_email_resp = client.post("/login", data={
        "username": test_email,
        "password": test_pass
    }, follow_redirects=False)
    assert login_email_resp.status_code == 302
    assert "/dashboard" in login_email_resp.headers["Location"]

def test_user_registration_mismatched_passwords(client):
    """Verify rejection when passwords do not match."""
    response = client.post("/register", data={
        "full_name": "Mismatch Tester",
        "username": "mismatch_user",
        "role": "placement_officer",
        "password": "Password123",
        "confirm_password": "DifferentPassword456"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Passwords do not match" in response.data

def test_user_registration_duplicate_username(client):
    """Verify rejection when attempting to register an already taken username (e.g. admin)."""
    response = client.post("/register", data={
        "full_name": "Admin Impersonator",
        "username": "admin",
        "role": "admin",
        "password": "NewPassword123",
        "confirm_password": "NewPassword123"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"already taken" in response.data

def test_google_login_custom_account(client):
    """Verify Google Login with custom user account email and auto-provisioning."""
    import time
    custom_email = f"student_{int(time.time())}@gmail.com"
    response = client.post("/google-login", data={
        "google_email": custom_email,
        "google_name": "Student Scholar",
        "role": "placement_officer"
    }, follow_redirects=False)

    assert response.status_code == 302
    assert "/dashboard" in response.headers["Location"]

    with client.session_transaction() as sess:
        assert sess.get("email") == custom_email
        assert sess.get("auth_provider") == "Google"
        assert sess.get("full_name") == "Student Scholar"

