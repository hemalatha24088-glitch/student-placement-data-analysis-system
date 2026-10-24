"""
Unit & Integration Tests for CSV Import Endpoints and Templates.
"""

import io

import pytest


def test_import_page_renders(officer_client):
    """Verify import portal renders upload cards and template links."""
    resp = officer_client.get("/import/")
    assert resp.status_code == 200
    assert b"CSV Data Import" in resp.data or b"Import" in resp.data


def test_import_students_valid_csv(officer_client):
    """Verify uploading a valid student CSV file."""
    csv_content = (
        "roll_no,student_name,department,graduation_year,cgpa,email,phone,gender,eligible_for_placement\n"
        "22IMP9001,Import Test Student,Computer Science and Engineering,2026,8.60,imp9001@college.edu,9876543210,Female,1\n"
    ).encode("utf-8")

    data = {"csv_file": (io.BytesIO(csv_content), "valid_students.csv")}
    resp = officer_client.post("/import/students", data=data, content_type="multipart/form-data")
    assert resp.status_code == 200
    assert b"Import" in resp.data


def test_import_students_invalid_extension(officer_client):
    """Verify rejection when file is not a .csv."""
    data = {"csv_file": (io.BytesIO(b"malicious executable"), "malicious.exe")}
    resp = officer_client.post("/import/students", data=data, content_type="multipart/form-data", follow_redirects=True)
    assert resp.status_code == 200
    assert b"must be a valid .csv" in resp.data


def test_import_placements_valid_csv(officer_client):
    """Verify uploading a valid placement offers CSV file."""
    csv_content = (
        "roll_no,company_name,role,package_amount,package_unit,placement_date,placement_year,status,offer_type,notes\n"
        "22IMP9001,Google,Software Engineer,35.00,LPA,2025-10-10,2026,Placed,Super Dream,Campus drive\n"
    ).encode("utf-8")

    data = {"csv_file": (io.BytesIO(csv_content), "valid_placements.csv")}
    resp = officer_client.post("/import/placements", data=data, content_type="multipart/form-data")
    assert resp.status_code == 200


def test_import_template_downloads(officer_client):
    """Verify CSV template generation for students and placements."""
    resp_stu = officer_client.get("/import/template/students")
    assert resp_stu.status_code == 200
    assert resp_stu.mimetype == "text/csv"
    assert b"roll_no" in resp_stu.data

    resp_plc = officer_client.get("/import/template/placements")
    assert resp_plc.status_code == 200
    assert resp_plc.mimetype == "text/csv"
    assert b"company_name" in resp_plc.data


def test_import_missing_file_validation(officer_client):
    """Verify flash error when no file is chosen or file part is missing."""
    resp1 = officer_client.post("/import/students", data={}, follow_redirects=True)
    assert resp1.status_code == 200
    assert b"No file" in resp1.data

    resp2 = officer_client.post("/import/placements", data={}, follow_redirects=True)
    assert resp2.status_code == 200
    assert b"No file" in resp2.data
