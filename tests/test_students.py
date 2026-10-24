"""
Unit tests for Student Management CRUD and business validations.
"""

import pytest

from app.services.student_service import (
    create_student,
    delete_student,
    get_student_by_id,
    get_student_by_roll_no,
    get_students,
    update_student,
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
        "eligible_for_placement": 1,
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
    invalid_data = {"roll_no": "", "student_name": "", "department": "", "graduation_year": None}
    success, msg = create_student(invalid_data)
    assert success is False
    assert "required" in msg.lower()


def test_student_routes_lifecycle(officer_client):
    """Verify end-to-end HTTP route lifecycle for student management."""
    import time

    unique_roll = f"STU{int(time.time() * 1000) % 100000}"

    # 1. Access Add Student page
    get_add = officer_client.get("/students/add")
    assert get_add.status_code == 200

    # 2. POST Add Student
    post_add = officer_client.post(
        "/students/add",
        data={
            "roll_no": unique_roll,
            "student_name": "Integration Test Student",
            "department": "Computer Science and Engineering",
            "graduation_year": "2026",
            "cgpa": "8.75",
            "email": f"{unique_roll.lower()}@college.edu",
            "phone": "9876543210",
            "gender": "Female",
            "eligible_for_placement": "1",
            "skills": ["1", "2"],
        },
        follow_redirects=True,
    )
    assert post_add.status_code == 200
    assert "Integration Test Student".encode() in post_add.data

    # Find the created student's ID
    stu = get_student_by_roll_no(unique_roll)
    assert stu is not None
    sid = stu["student_id"]

    # 3. View Student Profile
    view_resp = officer_client.get(f"/students/{sid}")
    assert view_resp.status_code == 200
    assert unique_roll.encode() in view_resp.data

    # 4. View Resume / Bio-Data
    resume_resp = officer_client.get(f"/students/{sid}/resume")
    assert resume_resp.status_code == 200
    assert unique_roll.encode() in resume_resp.data

    # 5. GET & POST Edit Student
    edit_get = officer_client.get(f"/students/{sid}/edit")
    assert edit_get.status_code == 200

    edit_post = officer_client.post(
        f"/students/{sid}/edit",
        data={
            "roll_no": unique_roll,
            "student_name": "Integration Test Student Updated",
            "department": "Information Technology",
            "graduation_year": "2026",
            "cgpa": "9.10",
            "email": f"{unique_roll.lower()}@college.edu",
            "phone": "9876543210",
            "gender": "Female",
            "eligible_for_placement": "1",
            "skills": ["1"],
        },
        follow_redirects=True,
    )
    assert edit_post.status_code == 200
    assert b"updated successfully" in edit_post.data

    # 6. Delete Student
    del_post = officer_client.post(f"/students/{sid}/delete", follow_redirects=True)
    assert del_post.status_code == 200
    assert b"deleted" in del_post.data.lower()
