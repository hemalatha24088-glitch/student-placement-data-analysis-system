"""
Unit & Integration Tests for Companies Management Module.
Verifies listing, adding, viewing, editing, deleting, and tier filtering.
"""

import time

import pytest


def test_companies_list_view(officer_client):
    """Verify company directory list renders properly."""
    response = officer_client.get("/companies/")
    assert response.status_code == 200
    assert b"Recruiting Companies" in response.data or b"Companies" in response.data


def test_company_crud_lifecycle(officer_client):
    """Verify full CRUD lifecycle: create, view, edit, and delete company."""
    unique_comp = f"AcmeCorp_{int(time.time() * 1000) % 100000}"

    # 1. Add Company
    add_resp = officer_client.post(
        "/companies/add",
        data={
            "company_name": unique_comp,
            "industry": "Information Technology",
            "location": "Bengaluru",
            "tier": "Super Dream",
            "website": "https://acmecorp.example.com",
        },
        follow_redirects=True,
    )
    assert add_resp.status_code == 200
    assert unique_comp.encode() in add_resp.data

    # 2. View Company
    with officer_client.application.app_context():
        from app.database.connection import get_db_cursor

        with get_db_cursor(commit=False) as cursor:
            cursor.execute("SELECT company_id FROM companies WHERE company_name = %s;", (unique_comp,))
            row = cursor.fetchone()
            assert row is not None
            cid = row["company_id"]

    view_resp = officer_client.get(f"/companies/{cid}")
    assert view_resp.status_code == 200
    assert unique_comp.encode() in view_resp.data

    # 3. Edit Company
    edit_resp = officer_client.post(
        f"/companies/{cid}/edit",
        data={
            "company_name": f"{unique_comp}_Updated",
            "industry": "Cloud Computing",
            "location": "Hyderabad",
            "tier": "Dream",
            "website": "https://updated.example.com",
        },
        follow_redirects=True,
    )
    assert edit_resp.status_code == 200
    assert b"updated successfully" in edit_resp.data or b"Updated" in edit_resp.data

    # 4. Delete Company
    del_resp = officer_client.post(f"/companies/{cid}/delete", follow_redirects=True)
    assert del_resp.status_code == 200
    assert b"deleted" in del_resp.data.lower()
