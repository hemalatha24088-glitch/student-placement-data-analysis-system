"""
Unit tests for CSV import validation and error diagnostics.
"""
import pytest
from app.services.import_service import (
    generate_student_csv_template,
    generate_placement_csv_template,
    import_students_csv,
    import_placements_csv
)

def test_csv_templates_generation():
    """Verify CSV sample templates contain standard required headers."""
    student_tmpl = generate_student_csv_template()
    assert "roll_no" in student_tmpl
    assert "student_name" in student_tmpl
    assert "department" in student_tmpl

    placement_tmpl = generate_placement_csv_template()
    assert "roll_no" in placement_tmpl
    assert "company_name" in placement_tmpl
    assert "package_amount" in placement_tmpl

def test_student_csv_validation_errors():
    """Verify that invalid rows (duplicate roll no, bad CGPA) are trapped and reported."""
    from app.services.student_service import get_student_by_roll_no, delete_student
    st = get_student_by_roll_no("22TESTCSV99")
    if st:
        delete_student(st["student_id"])

    # Row 1: Valid new student
    # Row 2: Bad CGPA (15.0)
    # Row 3: Duplicate existing roll no (22BCE1001)
    bad_csv_lines = [
        "roll_no,student_name,department,graduation_year,cgpa,email,phone,gender,eligible_for_placement",
        "22TESTCSV99,Test User New,Computer Science and Engineering,2026,8.5,t1@col.edu,9999,Other,1",
        "22TESTCSV98,Test User Two,Computer Science and Engineering,2026,15.5,t2@col.edu,9998,Other,1",
        "22BCE1001,Aarav Sharma Duplicate,Computer Science and Engineering,2026,9.0,aarav@col.edu,9997,Male,1"
    ]
    res = import_students_csv(bad_csv_lines)
    assert res["success"] is True
    assert res["imported_rows"] == 1
    assert res["failed_rows"] == 2
    # Cleanup
    st = get_student_by_roll_no("22TESTCSV99")
    if st:
        delete_student(st["student_id"])
