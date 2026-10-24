"""
Unit & Integration Tests for Placement Records CRUD and Offer Management.
"""

import time

import pytest

from app.database.connection import get_db_cursor


def test_placements_list_view(officer_client):
    """Verify placements index page renders properly."""
    response = officer_client.get("/placements/")
    assert response.status_code == 200
    assert b"Placement Records" in response.data or b"Placements" in response.data


def test_placement_crud_lifecycle(officer_client):
    """Verify creation, editing, and deletion of placement records."""
    # Lookup first student and company
    with get_db_cursor(commit=False) as cursor:
        cursor.execute("SELECT student_id FROM students WHERE eligible_for_placement = 1 LIMIT 1;")
        st = cursor.fetchone()
        cursor.execute("SELECT company_id FROM companies LIMIT 1;")
        co = cursor.fetchone()

    assert st is not None and co is not None
    sid = st["student_id"]
    cid = co["company_id"]

    # 1. Create Placement
    add_resp = officer_client.post(
        "/placements/add",
        data={
            "student_id": sid,
            "company_id": cid,
            "role": "Software Development Engineer",
            "package_amount": "14.50",
            "package_unit": "LPA",
            "placement_date": "2025-11-20",
            "placement_year": "2026",
            "status": "Placed",
            "offer_type": "Dream",
            "notes": "Automated pytest placement record",
        },
        follow_redirects=True,
    )
    assert add_resp.status_code == 200

    # Retrieve inserted placement id
    with get_db_cursor(commit=False) as cursor:
        cursor.execute(
            "SELECT placement_id FROM placements WHERE student_id = %s AND company_id = %s ORDER BY placement_id DESC LIMIT 1;",
            (sid, cid),
        )
        p = cursor.fetchone()
        assert p is not None
        pid = p["placement_id"]

    # 2. Edit Placement
    edit_resp = officer_client.post(
        f"/placements/{pid}/edit",
        data={
            "student_id": sid,
            "company_id": cid,
            "role": "Senior Software Development Engineer",
            "package_amount": "16.50",
            "package_unit": "LPA",
            "placement_date": "2025-11-25",
            "placement_year": "2026",
            "status": "Offer Accepted",
            "offer_type": "Super Dream",
            "notes": "Updated offer compensation",
        },
        follow_redirects=True,
    )
    assert edit_resp.status_code == 200
    assert b"updated successfully" in edit_resp.data or b"Senior Software" in edit_resp.data

    # 3. Delete Placement
    del_resp = officer_client.post(f"/placements/{pid}/delete", follow_redirects=True)
    assert del_resp.status_code == 200
    assert b"deleted successfully" in del_resp.data or b"deleted" in del_resp.data.lower()
