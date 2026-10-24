"""
Pytest configuration and fixtures for Student Placement Data Analysis System.
Provides app, client, authenticated sessions, and isolated test configurations.
"""
import sys
import os
import pytest

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from config import Config


class TestConfig(Config):
    TESTING = True
    DEBUG = False
    WTF_CSRF_ENABLED = False
    DEMO_MODE = True
    SECRET_KEY = "test-secret-key-for-pytest-execution"


@pytest.fixture
def app():
    """Create test application instance with CSRF disabled for functional testing."""
    test_app = create_app(TestConfig)
    test_app.config["TESTING"] = True
    test_app.config["WTF_CSRF_ENABLED"] = False
    test_app.config["DEMO_MODE"] = True
    return test_app


@pytest.fixture
def client(app):
    """Provide test client for making HTTP requests."""
    with app.test_client() as client:
        yield client


@pytest.fixture
def csrf_client():
    """Provide test client with CSRF protection enabled to verify rejection of untokened POSTs."""
    test_app = create_app(TestConfig)
    test_app.config["TESTING"] = True
    test_app.config["WTF_CSRF_ENABLED"] = True
    with test_app.test_client() as client:
        yield client


@pytest.fixture
def student_client(app):
    """Provide test client authenticated as a student."""
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["user_id"] = 999
            sess["username"] = "test_student"
            sess["role"] = "student"
            sess["student_id"] = 1
            sess["full_name"] = "Test Student"
        yield client


@pytest.fixture
def officer_client(app):
    """Provide test client authenticated as a placement officer."""
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["user_id"] = 998
            sess["username"] = "test_officer"
            sess["role"] = "placement_officer"
            sess["full_name"] = "Placement Officer"
        yield client


@pytest.fixture
def admin_client(app):
    """Provide test client authenticated as an administrator."""
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["user_id"] = 997
            sess["username"] = "test_admin"
            sess["role"] = "admin"
            sess["full_name"] = "System Admin"
        yield client
