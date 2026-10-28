"""
Student Service Module.
Handles student profile CRUD, searching, filtering, and skill associations.
"""

from app.database.connection import get_db_cursor


def get_all_departments():
    """Retrieve distinct departments from registered students."""
    try:
        with get_db_cursor(commit=False) as cursor:
            cursor.execute("SELECT DISTINCT department FROM students WHERE department IS NOT NULL ORDER BY department ASC;")
            rows = cursor.fetchall()
            return [r["department"] for r in rows]
    except Exception:
        return [
            "Computer Science and Engineering",
            "Artificial Intelligence & Data Science",
            "Information Technology",
            "Electronics & Communication Engineering",
        ]


def get_all_graduation_years():
    """Retrieve distinct graduation years from registered students."""
    try:
        with get_db_cursor(commit=False) as cursor:
            cursor.execute(
                "SELECT DISTINCT graduation_year FROM students WHERE graduation_year IS NOT NULL ORDER BY graduation_year DESC;"
            )
            rows = cursor.fetchall()
            return [r["graduation_year"] for r in rows]
    except Exception:
        return [2026, 2025, 2024, 2023]


def get_students(
    department=None, graduation_year=None, eligibility=None, search=None, page=1, per_page=15, sort_by="roll_no"
):
    """
    Retrieve paginated students matching optional search query and filters.
    """
    conditions = []
    params = []

    if department and department != "All":
        conditions.append("s.department = %s")
        params.append(department)

    if graduation_year and str(graduation_year) != "All":
        try:
            conditions.append("s.graduation_year = %s")
            params.append(int(graduation_year))
        except ValueError:
            pass

    if eligibility is not None and str(eligibility) != "All":
        if str(eligibility) in ("1", "true", "True", "Eligible"):
            conditions.append("s.eligible_for_placement = 1")
        elif str(eligibility) in ("0", "false", "False", "Ineligible"):
            conditions.append("s.eligible_for_placement = 0")

    if search:
        search_term = f"%{search.strip()}%"
        conditions.append("(s.roll_no LIKE %s OR s.student_name LIKE %s OR s.email LIKE %s)")
        params.extend([search_term, search_term, search_term])

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

    allowed_sorts = {
        "roll_no": "s.roll_no ASC",
        "name": "s.student_name ASC",
        "cgpa_desc": "s.cgpa DESC",
        "cgpa_asc": "s.cgpa ASC",
        "year_desc": "s.graduation_year DESC",
        "dept": "s.department ASC",
    }
    order_clause = allowed_sorts.get(sort_by, "s.roll_no ASC")

    # Count total
    count_sql = f"SELECT COUNT(*) AS total FROM students s {where_clause};"

    offset = max(0, (page - 1) * per_page)
    data_sql = f"""
        SELECT 
            s.*,
            (SELECT COUNT(*) FROM placements p WHERE p.student_id = s.student_id AND p.status IN ('Placed', 'Offer Accepted')) AS placed_offers_count,
            (SELECT COUNT(*) FROM student_skills ss WHERE ss.student_id = s.student_id) AS skill_count
        FROM students s
        {where_clause}
        ORDER BY {order_clause}
        LIMIT %s OFFSET %s;
    """

    with get_db_cursor(commit=False) as cursor:
        cursor.execute(count_sql, params)
        total = cursor.fetchone()["total"]

        paged_params = list(params) + [per_page, offset]
        cursor.execute(data_sql, paged_params)
        students = cursor.fetchall()

    total_pages = (total + per_page - 1) // per_page if total > 0 else 1

    return {"students": students, "total": total, "page": page, "per_page": per_page, "total_pages": total_pages}


def get_student_by_id(student_id):
    """Retrieve complete profile of a student by primary key ID."""
    with get_db_cursor(commit=False) as cursor:
        cursor.execute("SELECT * FROM students WHERE student_id = %s;", (student_id,))
        student = cursor.fetchone()
        if not student:
            return None

        # Fetch skills
        cursor.execute(
            """
            SELECT s.skill_id, s.skill_name, s.skill_category, ss.proficiency_level
            FROM student_skills ss
            JOIN skills s ON ss.skill_id = s.skill_id
            WHERE ss.student_id = %s
            ORDER BY s.skill_name ASC;
        """,
            (student_id,),
        )
        student["skills"] = cursor.fetchall()

        # Fetch placements
        cursor.execute(
            """
            SELECT p.*, c.company_name, c.tier, c.industry
            FROM placements p
            JOIN companies c ON p.company_id = c.company_id
            WHERE p.student_id = %s
            ORDER BY p.placement_date DESC;
        """,
            (student_id,),
        )
        student["placements"] = cursor.fetchall()

        return student


def get_student_by_roll_no(roll_no):
    """Check for existence by roll number."""
    with get_db_cursor(commit=False) as cursor:
        cursor.execute("SELECT * FROM students WHERE roll_no = %s;", (roll_no.strip(),))
        return cursor.fetchone()


def create_student(data, skill_ids=None):
    """
    Register a new student with validation against duplicate roll number.
    Returns (success: bool, student_id or error_msg).
    """
    roll_no = data.get("roll_no", "").strip().upper()
    name = data.get("student_name", "").strip()
    dept = data.get("department", "").strip()
    year = data.get("graduation_year")
    cgpa = data.get("cgpa")
    email = data.get("email", "").strip() or None
    phone = data.get("phone", "").strip() or None
    gender = data.get("gender", "Other")
    eligible = 1 if data.get("eligible_for_placement") in (1, "1", True, "true", "on") else 0

    if not roll_no or not name or not dept or not year:
        return False, "Roll number, Name, Department, and Graduation Year are required."

    if get_student_by_roll_no(roll_no):
        return False, f"A student with Roll Number '{roll_no}' already exists in the system."

    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            """
            INSERT INTO students (roll_no, student_name, department, graduation_year, cgpa, email, phone, gender, eligible_for_placement)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """,
            (roll_no, name, dept, year, cgpa, email, phone, gender, eligible),
        )
        student_id = cursor.lastrowid

        if skill_ids:
            for sid in skill_ids:
                try:
                    cursor.execute(
                        """
                        INSERT IGNORE INTO student_skills (student_id, skill_id, proficiency_level)
                        VALUES (%s, %s, 'Intermediate');
                    """,
                        (student_id, int(sid)),
                    )
                except Exception:
                    pass

    return True, student_id


def update_student(student_id, data, skill_ids=None):
    """
    Update existing student record with roll number uniqueness protection.
    """
    existing = get_student_by_id(student_id)
    if not existing:
        return False, f"Student ID {student_id} not found."

    roll_no = data.get("roll_no", "").strip().upper()
    name = data.get("student_name", "").strip()
    dept = data.get("department", "").strip()
    year = data.get("graduation_year")
    cgpa = data.get("cgpa")
    email = data.get("email", "").strip() or None
    phone = data.get("phone", "").strip() or None
    gender = data.get("gender", existing.get("gender", "Other"))
    eligible = 1 if data.get("eligible_for_placement") in (1, "1", True, "true", "on") else 0

    if not roll_no or not name or not dept or not year:
        return False, "Roll number, Name, Department, and Graduation Year are required."

    # Check roll_no conflict with other students
    conflict = get_student_by_roll_no(roll_no)
    if conflict and conflict["student_id"] != int(student_id):
        return False, f"Another student already uses Roll Number '{roll_no}'."

    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            """
            UPDATE students
            SET roll_no = %s, student_name = %s, department = %s, graduation_year = %s,
                cgpa = %s, email = %s, phone = %s, gender = %s, eligible_for_placement = %s
            WHERE student_id = %s;
        """,
            (roll_no, name, dept, year, cgpa, email, phone, gender, eligible, student_id),
        )

        if skill_ids is not None:
            # Refresh skills
            cursor.execute("DELETE FROM student_skills WHERE student_id = %s;", (student_id,))
            for sid in skill_ids:
                try:
                    cursor.execute(
                        """
                        INSERT INTO student_skills (student_id, skill_id, proficiency_level)
                        VALUES (%s, %s, 'Intermediate');
                    """,
                        (student_id, int(sid)),
                    )
                except Exception:
                    pass

    return True, student_id


def delete_student(student_id):
    """Delete student and all cascaded foreign relations."""
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("DELETE FROM students WHERE student_id = %s;", (student_id,))
        affected = cursor.rowcount
    return affected > 0


def get_all_students_simple():
    """Retrieve simple list of registered students for dropdowns and selectors."""
    with get_db_cursor(commit=False) as cursor:
        cursor.execute("""
            SELECT s.student_id, s.roll_no, s.student_name, s.department, s.cgpa,
                   CASE WHEN COUNT(p.placement_id) > 0 THEN 'Placed' ELSE 'Unplaced' END AS placement_status
            FROM students s
            LEFT JOIN placements p ON s.student_id = p.student_id AND p.status IN ('Placed', 'Offer Accepted')
            GROUP BY s.student_id
            ORDER BY s.student_name ASC;
        """)
        return cursor.fetchall()
