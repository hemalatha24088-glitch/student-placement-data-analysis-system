"""
Placement Service Module.
Handles placement job offer records, status transitions, duplicate checking, and pagination.
"""

from datetime import datetime

from app.database.connection import get_db_cursor

VALID_STATUSES = ["Placed", "Offer Accepted", "Offer Pending", "Rejected"]
VALID_OFFER_TYPES = ["Full-time", "Internship + PPO", "Super Dream", "Dream", "Mass / IT Services", "Core Engineering"]


def get_placements(
    department=None, graduation_year=None, company_id=None, status=None, search=None, page=1, per_page=15
):
    """
    Retrieve paginated placement offers with joined student and company data.
    """
    conditions = []
    params = []

    if department and department != "All":
        conditions.append("s.department = %s")
        params.append(department)

    if graduation_year and str(graduation_year) != "All":
        try:
            conditions.append("p.placement_year = %s")
            params.append(int(graduation_year))
        except ValueError:
            pass

    if company_id and str(company_id) != "All":
        try:
            conditions.append("p.company_id = %s")
            params.append(int(company_id))
        except ValueError:
            pass

    if status and status != "All":
        conditions.append("p.status = %s")
        params.append(status)

    if search:
        search_term = f"%{search.strip()}%"
        conditions.append("(s.roll_no LIKE %s OR s.student_name LIKE %s OR c.company_name LIKE %s OR p.role LIKE %s)")
        params.extend([search_term, search_term, search_term, search_term])

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

    count_sql = f"""
        SELECT COUNT(*) AS total
        FROM placements p
        JOIN students s ON p.student_id = s.student_id
        JOIN companies c ON p.company_id = c.company_id
        {where_clause};
    """

    offset = max(0, (page - 1) * per_page)
    data_sql = f"""
        SELECT 
            p.*,
            s.student_name,
            s.roll_no,
            s.department,
            s.graduation_year,
            c.company_name,
            c.industry,
            c.tier
        FROM placements p
        JOIN students s ON p.student_id = s.student_id
        JOIN companies c ON p.company_id = c.company_id
        {where_clause}
        ORDER BY p.placement_date DESC, p.package_amount DESC
        LIMIT %s OFFSET %s;
    """

    with get_db_cursor(commit=False) as cursor:
        cursor.execute(count_sql, params)
        total = cursor.fetchone()["total"]

        paged_params = list(params) + [per_page, offset]
        cursor.execute(data_sql, paged_params)
        placements = cursor.fetchall()

    total_pages = (total + per_page - 1) // per_page if total > 0 else 1

    return {"placements": placements, "total": total, "page": page, "per_page": per_page, "total_pages": total_pages}


def get_placement_by_id(placement_id):
    """Retrieve full placement offer by ID."""
    with get_db_cursor(commit=False) as cursor:
        cursor.execute(
            """
            SELECT p.*, s.student_name, s.roll_no, s.department, s.graduation_year,
                   c.company_name, c.tier
            FROM placements p
            JOIN students s ON p.student_id = s.student_id
            JOIN companies c ON p.company_id = c.company_id
            WHERE p.placement_id = %s;
        """,
            (placement_id,),
        )
        return cursor.fetchone()


def check_duplicate_placement(student_id, company_id, role, placement_year, exclude_placement_id=None):
    """
    Enforce business rule: A student cannot have multiple offers from the same
    company for the exact same role in the same placement year.
    """
    sql = """
        SELECT placement_id FROM placements
        WHERE student_id = %s AND company_id = %s AND LOWER(role) = LOWER(%s) AND placement_year = %s
    """
    params = [student_id, company_id, role.strip(), placement_year]
    if exclude_placement_id:
        sql += " AND placement_id != %s"
        params.append(exclude_placement_id)

    with get_db_cursor(commit=False) as cursor:
        cursor.execute(sql, params)
        return cursor.fetchone() is not None


def create_placement(data):
    """
    Create a new placement record with validation.
    Returns (success: bool, placement_id or error_msg).
    """
    try:
        student_id = int(data.get("student_id"))
        company_id = int(data.get("company_id"))
        role = data.get("role", "").strip()
        package_amount = float(data.get("package_amount"))
        package_unit = data.get("package_unit", "LPA").strip()
        placement_date = data.get("placement_date")
        placement_year = int(data.get("placement_year", datetime.now().year))
        status = data.get("status", "Placed").strip()
        offer_type = data.get("offer_type", "Full-time").strip()
        notes = data.get("notes", "").strip() or None
    except (ValueError, TypeError) as e:
        return False, f"Invalid input format: {str(e)}"

    if not role:
        return False, "Job role is required."

    if package_amount <= 0 or package_amount > 200.0:
        return False, "Package amount must be greater than 0 and realistic (up to 200 LPA)."

    if status not in VALID_STATUSES:
        return False, f"Status must be one of: {', '.join(VALID_STATUSES)}"

    # Check student existence
    with get_db_cursor(commit=False) as cursor:
        cursor.execute(
            "SELECT student_id, eligible_for_placement, student_name FROM students WHERE student_id = %s;",
            (student_id,),
        )
        student = cursor.fetchone()
        if not student:
            return False, "Selected student does not exist."

        cursor.execute("SELECT company_id, company_name FROM companies WHERE company_id = %s;", (company_id,))
        company = cursor.fetchone()
        if not company:
            return False, "Selected company does not exist."

    # Enforce duplicate rule
    if check_duplicate_placement(student_id, company_id, role, placement_year):
        return (
            False,
            f"Duplicate offer detected: {student['student_name']} already has an offer from {company['company_name']} for '{role}' in {placement_year}.",
        )

    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            """
            INSERT INTO placements (student_id, company_id, role, package_amount, package_unit,
                                    placement_date, placement_year, status, offer_type, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """,
            (
                student_id,
                company_id,
                role,
                package_amount,
                package_unit,
                placement_date,
                placement_year,
                status,
                offer_type,
                notes,
            ),
        )
        return True, cursor.lastrowid


def update_placement(placement_id, data):
    """Update placement record."""
    try:
        student_id = int(data.get("student_id"))
        company_id = int(data.get("company_id"))
        role = data.get("role", "").strip()
        package_amount = float(data.get("package_amount"))
        package_unit = data.get("package_unit", "LPA").strip()
        placement_date = data.get("placement_date")
        placement_year = int(data.get("placement_year"))
        status = data.get("status", "Placed").strip()
        offer_type = data.get("offer_type", "Full-time").strip()
        notes = data.get("notes", "").strip() or None
    except (ValueError, TypeError) as e:
        return False, f"Invalid input format: {str(e)}"

    if not role:
        return False, "Job role is required."

    if package_amount <= 0 or package_amount > 200.0:
        return False, "Package amount must be greater than 0 and realistic (up to 200 LPA)."

    if status not in VALID_STATUSES:
        return False, f"Status must be one of: {', '.join(VALID_STATUSES)}"

    if check_duplicate_placement(student_id, company_id, role, placement_year, exclude_placement_id=placement_id):
        return False, "Duplicate offer detected for the same student, company, role, and year."

    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            """
            UPDATE placements
            SET student_id = %s, company_id = %s, role = %s, package_amount = %s,
                package_unit = %s, placement_date = %s, placement_year = %s,
                status = %s, offer_type = %s, notes = %s
            WHERE placement_id = %s;
        """,
            (
                student_id,
                company_id,
                role,
                package_amount,
                package_unit,
                placement_date,
                placement_year,
                status,
                offer_type,
                notes,
                placement_id,
            ),
        )
        return True, placement_id


def delete_placement(placement_id):
    """Delete a placement record."""
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("DELETE FROM placements WHERE placement_id = %s;", (placement_id,))
        return cursor.rowcount > 0


def get_recent_placements(limit=6):
    """Retrieve recent placements for the dashboard."""
    with get_db_cursor(commit=False) as cursor:
        cursor.execute(
            """
            SELECT p.*, s.student_name, s.roll_no, s.department, c.company_name, c.tier
            FROM placements p
            JOIN students s ON p.student_id = s.student_id
            JOIN companies c ON p.company_id = c.company_id
            WHERE p.status IN ('Placed', 'Offer Accepted')
            ORDER BY p.placement_date DESC
            LIMIT %s;
        """,
            (limit,),
        )
        return cursor.fetchall()
