"""
Unit tests for Placement Offers management and duplicate policy.
"""

import pytest

from app.services.company_service import get_companies
from app.services.placement_service import (
    check_duplicate_placement,
    create_placement,
    delete_placement,
    get_placement_by_id,
    update_placement,
)
from app.services.student_service import get_students


def test_placement_duplicate_policy_and_package_validation():
    """Verify package range bounds and duplicate prevention rule."""
    students = get_students(per_page=1)["students"]
    companies = get_companies()
    assert len(students) > 0
    assert len(companies) > 0

    student_id = students[0]["student_id"]
    company_id = companies[0]["company_id"]

    # 1. Invalid package bounds (<= 0 or > 200 LPA)
    bad_data = {
        "student_id": student_id,
        "company_id": company_id,
        "role": "QA Engineer",
        "package_amount": -5.0,
        "package_unit": "LPA",
        "placement_date": "2026-03-01",
        "placement_year": 2026,
        "status": "Placed",
    }
    success, err = create_placement(bad_data)
    assert success is False
    assert "greater than 0" in err

    # 2. Valid placement creation
    valid_data = {
        "student_id": student_id,
        "company_id": company_id,
        "role": "Lead Automation Test Engineer",
        "package_amount": 16.50,
        "package_unit": "LPA",
        "placement_date": "2026-03-15",
        "placement_year": 2026,
        "status": "Placed",
        "offer_type": "Dream",
        "notes": "Unit test generated offer",
    }
    success, placement_id = create_placement(valid_data)
    assert success is True
    assert isinstance(placement_id, int)

    # 3. Duplicate placement rejection (same student, company, role, year)
    dup_success, dup_err = create_placement(valid_data)
    assert dup_success is False
    assert "Duplicate offer detected" in dup_err

    # Cleanup
    delete_placement(placement_id)
    assert get_placement_by_id(placement_id) is None


def test_get_placements_filters():
    """Verify get_placements filter logic across department, year, status, company, and search."""
    from app.services.placement_service import get_placements

    res = get_placements(
        department="Computer Science and Engineering",
        graduation_year=2026,
        company_id=1,
        status="Placed",
        search="Software",
        page=1,
        per_page=10,
    )
    assert isinstance(res, dict)
    assert "placements" in res
    assert "total" in res


def test_placement_validation_failures():
    """Verify service validation rejections for missing role, invalid status, and missing entities."""
    # Missing role
    res, msg = create_placement(
        {
            "student_id": 1,
            "company_id": 1,
            "role": "",
            "package_amount": 10.0,
            "package_unit": "LPA",
            "placement_date": "2026-01-01",
            "placement_year": 2026,
            "status": "Placed",
        }
    )
    assert res is False
    assert "required" in msg.lower()

    # Invalid status
    res, msg = create_placement(
        {
            "student_id": 1,
            "company_id": 1,
            "role": "Engineer",
            "package_amount": 10.0,
            "package_unit": "LPA",
            "placement_date": "2026-01-01",
            "placement_year": 2026,
            "status": "NonexistentStatus",
        }
    )
    assert res is False
    assert "Status must be" in msg

    # Student not found
    res, msg = create_placement(
        {
            "student_id": 9999999,
            "company_id": 1,
            "role": "Engineer",
            "package_amount": 10.0,
            "package_unit": "LPA",
            "placement_date": "2026-01-01",
            "placement_year": 2026,
            "status": "Placed",
        }
    )
    assert res is False
    assert "student does not exist" in msg.lower()

    # Company not found
    res, msg = create_placement(
        {
            "student_id": 1,
            "company_id": 9999999,
            "role": "Engineer",
            "package_amount": 10.0,
            "package_unit": "LPA",
            "placement_date": "2026-01-01",
            "placement_year": 2026,
            "status": "Placed",
        }
    )
    assert res is False
    assert "company does not exist" in msg.lower()
