"""
Unit & Integration Tests for Administrator User Management Portal.
Validates role promotion, administrative password resets, and user deletion.
"""

import time

import pytest
from werkzeug.security import generate_password_hash

from app.database.connection import get_db_cursor


def test_admin_user_management_portal_renders(admin_client):
    """Verify administrator user management directory loads properly."""
    response = admin_client.get("/admin/users")
    assert response.status_code == 200
    assert b"User Management" in response.data or b"System Users" in response.data


def test_admin_role_promotion_and_password_reset(admin_client):
    """Verify administrator can promote a student to placement officer and reset user password."""
    unique_user = f"admintest_{int(time.time() * 1000) % 100000}"
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            """
            INSERT INTO users (username, password_hash, full_name, role, email)
            VALUES (%s, %s, 'Admin Test Subject', 'student', %s);
            """,
            (unique_user, generate_password_hash("InitialPass123!"), f"{unique_user}@test.edu"),
        )
        uid = cursor.lastrowid

    # 1. Promote to Placement Officer
    role_resp = admin_client.post(f"/admin/users/{uid}/role", data={"role": "placement_officer"}, follow_redirects=True)
    assert role_resp.status_code == 200
    assert b"role updated" in role_resp.data.lower()

    # 2. Reset Password
    reset_resp = admin_client.post(
        f"/admin/users/{uid}/reset-password", data={"new_password": "NewSecretPassword123!"}, follow_redirects=True
    )
    assert reset_resp.status_code == 200
    assert b"password reset" in reset_resp.data.lower() or b"successfully" in reset_resp.data.lower()

    # 3. Delete User
    del_resp = admin_client.post(f"/admin/users/{uid}/delete", follow_redirects=True)
    assert del_resp.status_code == 200
    assert b"deleted" in del_resp.data.lower()


def test_admin_edge_cases_and_safeguards(admin_client):
    """Verify safeguards: self-demotion block, self-deletion block, invalid role, short password."""
    # 1. Invalid role
    inv_role = admin_client.post("/admin/users/999/role", data={"role": "supergod"}, follow_redirects=True)
    assert inv_role.status_code == 200
    assert b"Invalid role" in inv_role.data

    # 2. Self demotion block (admin_client has user_id = 997)
    demote_self = admin_client.post("/admin/users/997/role", data={"role": "student"}, follow_redirects=True)
    assert demote_self.status_code == 200
    assert b"cannot demote" in demote_self.data

    # 3. Self deletion block
    del_self = admin_client.post("/admin/users/997/delete", follow_redirects=True)
    assert del_self.status_code == 200
    assert b"cannot delete" in del_self.data

    # 4. Short password on reset
    short_pw = admin_client.post(
        "/admin/users/999/reset-password", data={"new_password": "short"}, follow_redirects=True
    )
    assert short_pw.status_code == 200
    assert b"at least 8 characters" in short_pw.data
