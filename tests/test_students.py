"""
Unit tests for Student Management CRUD and business validations.
"""
import pytest
from app.services.student_service import (
    create_student,
    get_student_by_id,
    get_student_by_roll_no,
    update_student,
    delete_student,
    get_students
)

def test_student_crud_lifecycle():
    """Test full lifecycle: create, read, update, delete."""
    test_roll = "TEST9999"

    # Clean up prior test run if any
    existing = get_student_by_roll_no(test_roll)
    if existing:
        delete_student(existing["student_id"])

    # 1. Create
    data = {
        "roll_no": test_roll,
        "student_name": "Automated Tester",
        "department": "Computer Science and Engineering",
        "graduation_year": 2026,
        "cgpa": 8.95,
        "email": "autotest@college.edu",
        "phone": "9998887776",
        "gender": "Other",
        "eligible_for_placement": 1
    }
    success, student_id = create_student(data)
    assert success is True
    assert isinstance(student_id, int)

    # 2. Read
    student = get_student_by_id(student_id)
    assert student is not None
    assert student["student_name"] == "Automated Tester"
    assert student["roll_no"] == test_roll
    assert float(student["cgpa"]) == 8.95

    # 3. Duplicate Roll No Rejection
    dup_success, dup_err = create_student(data)
    assert dup_success is False
    assert "already exists" in dup_err

    # 4. Update
    data["student_name"] = "Automated Tester Updated"
    data["cgpa"] = 9.20
    up_success, up_id = update_student(student_id, data)
    assert up_success is True

    updated_student = get_student_by_id(student_id)
    assert updated_student["student_name"] == "Automated Tester Updated"
    assert float(updated_student["cgpa"]) == 9.20

    # 5. Delete
    del_res = delete_student(student_id)
    assert del_res is True

    # Verify deleted
    assert get_student_by_id(student_id) is None

def test_student_required_fields_validation():
    """Verify validation when mandatory fields are omitted."""
    invalid_data = {
        "roll_no": "",
        "student_name": "",
        "department": "",
        "graduation_year": None
    }
    success, msg = create_student(invalid_data)
    assert success is False
    assert "required" in msg.lower()
