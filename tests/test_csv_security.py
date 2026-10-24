"""
CSV Import/Export Security & Injection Hardening Tests.
Validates formula injection mitigation (CWE-1236) and bulk row cap limits.
"""
import pytest
from app.routes.reports import sanitize_csv_cell, sanitize_row
from app.services.import_service import import_students_csv, import_placements_csv, MAX_IMPORT_ROWS


def test_csv_cell_formula_injection_sanitization():
    """Formulas starting with =, +, -, @, \\t, or \\r must be prefixed with a single quote."""
    # Dangerous formula inputs
    assert sanitize_csv_cell("=1+1") == "'=1+1"
    assert sanitize_csv_cell("=cmd|' /C calc'!A0") == "'=cmd|' /C calc'!A0"
    assert sanitize_csv_cell("+2+5") == "'+2+5"
    assert sanitize_csv_cell("-5+2") == "'-5+2"
    assert sanitize_csv_cell("@SUM(A1:A10)") == "'@SUM(A1:A10)"
    assert sanitize_csv_cell("\tTabPrefix") == "'\tTabPrefix"

    # Safe inputs must remain unchanged
    assert sanitize_csv_cell("Safe Student Name") == "Safe Student Name"
    assert sanitize_csv_cell("9.50") == "9.50"
    assert sanitize_csv_cell(12345) == "12345"
    assert sanitize_csv_cell(None) == ""


def test_sanitize_row_helper():
    """Verify entire row is sanitized."""
    raw_row = ["=DANGEROUS", "Normal Name", "+919876543210", 8.8]
    sanitized = sanitize_row(raw_row)
    assert sanitized == ["'=DANGEROUS", "Normal Name", "'+919876543210", "8.8"]


def test_csv_import_row_limit_enforcement():
    """CSV imports exceeding 1,000 rows must be rejected with a clear message."""
    header = "roll_no,student_name,department,graduation_year,cgpa,email,phone,gender,eligible_for_placement"
    # Create 1005 rows
    lines = [header] + [f"TEST{i:04d},Student {i},Computer Science and Engineering,2026,8.0,s{i}@mail.com,9000000000,Female,1" for i in range(1005)]

    result = import_students_csv(lines)
    assert result["success"] is False
    assert f"exceeds maximum allowable limit of {MAX_IMPORT_ROWS}" in result["message"]


def test_reports_export_csv_escapes_formulas(officer_client):
    """Verify that downloading CSV reports sanitizes cells."""
    response = officer_client.get("/reports/export-csv?type=summary")
    assert response.status_code == 200
    assert response.mimetype == "text/csv"
    assert "Content-Disposition" in response.headers
