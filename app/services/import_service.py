"""
CSV Import and Export Service Module.
Handles validation, duplicate detection, row-by-row error reporting,
and sample template generation.
"""
import io
import csv
from datetime import datetime
from app.database.connection import get_db_cursor
from app.services.student_service import get_student_by_roll_no
from app.services.placement_service import check_duplicate_placement, VALID_STATUSES, VALID_OFFER_TYPES

STUDENT_CSV_HEADERS = ["roll_no", "student_name", "department", "graduation_year", "cgpa", "email", "phone", "gender", "eligible_for_placement"]
PLACEMENT_CSV_HEADERS = ["roll_no", "company_name", "role", "package_amount", "package_unit", "placement_date", "placement_year", "status", "offer_type", "notes"]

def generate_student_csv_template():
    """Generate sample CSV template string for student bulk upload."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(STUDENT_CSV_HEADERS)
    writer.writerow(["22BCE1099", "Sample Student", "Computer Science and Engineering", 2026, 8.50, "sample@college.edu", "9876543299", "Female", 1])
    writer.writerow(["22AML1099", "Candidate Two", "Artificial Intelligence and Machine Learning", 2026, 9.10, "cand2@college.edu", "9876543298", "Male", 1])
    return output.getvalue()

def generate_placement_csv_template():
    """Generate sample CSV template string for placement bulk upload."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(PLACEMENT_CSV_HEADERS)
    writer.writerow(["22BCE1099", "Microsoft", "Software Engineer", 24.50, "LPA", "2025-10-15", 2026, "Placed", "Super Dream", "Campus hire"])
    writer.writerow(["22AML1099", "NVIDIA", "AI Research Engineer", 38.00, "LPA", "2025-09-20", 2026, "Placed", "Super Dream", "Research drive"])
    return output.getvalue()

def import_students_csv(file_stream):
    """
    Validate and insert student records from CSV.
    Returns:
    {
        "success": bool,
        "total_rows": int,
        "imported_rows": int,
        "failed_rows": int,
        "errors": list of {"row": int, "roll_no": str, "reason": str}
    }
    """
    reader = csv.DictReader(file_stream)
    if not reader.fieldnames:
        return {"success": False, "message": "Uploaded CSV file is empty."}

    # Verify header subset
    required_cols = {"roll_no", "student_name", "department", "graduation_year"}
    missing = required_cols - set(reader.fieldnames)
    if missing:
        return {"success": False, "message": f"Missing required CSV columns: {', '.join(missing)}"}

    total_rows = 0
    imported = 0
    errors = []

    rows_to_insert = []

    for idx, row in enumerate(reader, start=2):
        total_rows += 1
        roll_no = row.get("roll_no", "").strip().upper()
        name = row.get("student_name", "").strip()
        dept = row.get("department", "").strip()
        year_str = row.get("graduation_year", "").strip()

        if not roll_no:
            errors.append({"row": idx, "roll_no": roll_no, "reason": "Missing roll number."})
            continue

        if not name:
            errors.append({"row": idx, "roll_no": roll_no, "reason": "Missing student name."})
            continue

        if not dept:
            errors.append({"row": idx, "roll_no": roll_no, "reason": "Missing department."})
            continue

        try:
            year = int(year_str)
            if year < 2000 or year > 2040:
                raise ValueError()
        except ValueError:
            errors.append({"row": idx, "roll_no": roll_no, "reason": f"Invalid graduation year '{year_str}'."})
            continue

        # CGPA
        cgpa_str = row.get("cgpa", "").strip()
        cgpa = None
        if cgpa_str:
            try:
                cgpa = float(cgpa_str)
                if cgpa < 0.0 or cgpa > 10.0:
                    raise ValueError()
            except ValueError:
                errors.append({"row": idx, "roll_no": roll_no, "reason": f"CGPA must be between 0.0 and 10.0 (got '{cgpa_str}')."})
                continue

        # Eligibility
        elig_str = row.get("eligible_for_placement", "1").strip().lower()
        eligible = 1 if elig_str in ("1", "true", "yes", "eligible") else 0

        # Check existing roll_no
        if get_student_by_roll_no(roll_no):
            errors.append({"row": idx, "roll_no": roll_no, "reason": f"Student with roll number '{roll_no}' already exists in database."})
            continue

        email = row.get("email", "").strip() or None
        phone = row.get("phone", "").strip() or None
        gender = row.get("gender", "Other").strip() or "Other"

        rows_to_insert.append((roll_no, name, dept, year, cgpa, email, phone, gender, eligible))

    # Perform insertions
    if rows_to_insert:
        with get_db_cursor(commit=True) as cursor:
            for r in rows_to_insert:
                cursor.execute("""
                    INSERT INTO students (roll_no, student_name, department, graduation_year, cgpa, email, phone, gender, eligible_for_placement)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                """, r)
                imported += 1

    return {
        "success": True,
        "total_rows": total_rows,
        "imported_rows": imported,
        "failed_rows": len(errors),
        "errors": errors
    }

def import_placements_csv(file_stream):
    """
    Validate and insert placement records from CSV.
    """
    reader = csv.DictReader(file_stream)
    if not reader.fieldnames:
        return {"success": False, "message": "Uploaded CSV file is empty."}

    required_cols = {"roll_no", "company_name", "role", "package_amount"}
    missing = required_cols - set(reader.fieldnames)
    if missing:
        return {"success": False, "message": f"Missing required CSV columns: {', '.join(missing)}"}

    total_rows = 0
    imported = 0
    errors = []
    rows_to_insert = []

    # Cache companies map
    with get_db_cursor(commit=False) as cursor:
        cursor.execute("SELECT company_id, LOWER(company_name) AS norm_name FROM companies;")
        comp_map = {r["norm_name"]: r["company_id"] for r in cursor.fetchall()}

    for idx, row in enumerate(reader, start=2):
        total_rows += 1
        roll_no = row.get("roll_no", "").strip().upper()
        comp_name = row.get("company_name", "").strip()
        role = row.get("role", "").strip()
        pkg_str = row.get("package_amount", "").strip()

        if not roll_no or not comp_name or not role or not pkg_str:
            errors.append({"row": idx, "roll_no": roll_no, "reason": "Roll No, Company, Role, and Package are mandatory."})
            continue

        # Look up student
        student = get_student_by_roll_no(roll_no)
        if not student:
            errors.append({"row": idx, "roll_no": roll_no, "reason": f"Student with Roll No '{roll_no}' not found in database."})
            continue

        # Look up or auto-register company
        norm_comp = comp_name.lower()
        company_id = comp_map.get(norm_comp)
        if not company_id:
            # Auto-insert company
            with get_db_cursor(commit=True) as cursor:
                cursor.execute("INSERT INTO companies (company_name, industry) VALUES (%s, 'Information Technology');", (comp_name,))
                company_id = cursor.lastrowid
                comp_map[norm_comp] = company_id

        # Package validation
        try:
            pkg = float(pkg_str)
            if pkg <= 0 or pkg > 200.0:
                raise ValueError()
        except ValueError:
            errors.append({"row": idx, "roll_no": roll_no, "reason": f"Package amount must be between 0 and 200 LPA (got '{pkg_str}')."})
            continue

        unit = row.get("package_unit", "LPA").strip() or "LPA"
        
        # Placement Date
        date_str = row.get("placement_date", "").strip()
        try:
            p_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else datetime.now().date()
        except ValueError:
            errors.append({"row": idx, "roll_no": roll_no, "reason": f"Invalid date format for '{date_str}', expected YYYY-MM-DD."})
            continue

        year_str = row.get("placement_year", "").strip()
        p_year = int(year_str) if year_str and year_str.isdigit() else p_date.year

        status = row.get("status", "Placed").strip()
        if status not in VALID_STATUSES:
            status = "Placed"

        offer_type = row.get("offer_type", "Full-time").strip() or "Full-time"
        notes = row.get("notes", "").strip() or None

        # Duplicate check
        if check_duplicate_placement(student["student_id"], company_id, role, p_year):
            errors.append({"row": idx, "roll_no": roll_no, "reason": f"Duplicate offer: student already has an offer from {comp_name} for '{role}' in {p_year}."})
            continue

        rows_to_insert.append((student["student_id"], company_id, role, pkg, unit, p_date, p_year, status, offer_type, notes))

    if rows_to_insert:
        with get_db_cursor(commit=True) as cursor:
            for r in rows_to_insert:
                cursor.execute("""
                    INSERT INTO placements (student_id, company_id, role, package_amount, package_unit,
                                            placement_date, placement_year, status, offer_type, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """, r)
                imported += 1

    return {
        "success": True,
        "total_rows": total_rows,
        "imported_rows": imported,
        "failed_rows": len(errors),
        "errors": errors
    }
