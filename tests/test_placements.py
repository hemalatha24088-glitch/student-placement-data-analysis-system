"""
Unit tests for Placement Offers management and duplicate policy.
"""
import pytest
from app.services.placement_service import (
    create_placement,
    get_placement_by_id,
    update_placement,
    delete_placement,
    check_duplicate_placement
)
from app.services.student_service import get_students
from app.services.company_service import get_companies

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
        "status": "Placed"
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
        "notes": "Unit test generated offer"
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
