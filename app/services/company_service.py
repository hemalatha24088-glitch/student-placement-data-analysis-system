"""
Company Service Module.
Handles recruiting partner companies and recruitment aggregation.
"""
from app.database.connection import get_db_cursor

def get_companies(search=None, industry=None):
    """Retrieve companies with hiring statistics and average CTC offered."""
    conditions = []
    params = []

    if search:
        conditions.append("(c.company_name LIKE %s OR c.location LIKE %s OR c.industry LIKE %s)")
        term = f"%{search.strip()}%"
        params.extend([term, term, term])

    if industry and industry != "All":
        conditions.append("c.industry = %s")
        params.append(industry)

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

    query = f"""
        SELECT 
            c.*,
            COUNT(p.placement_id) AS total_offers,
            COUNT(DISTINCT p.student_id) AS distinct_students_hired,
            ROUND(AVG(CASE WHEN p.status IN ('Placed', 'Offer Accepted') THEN p.package_amount ELSE NULL END), 2) AS avg_package_lpa,
            MAX(CASE WHEN p.status IN ('Placed', 'Offer Accepted') THEN p.package_amount ELSE NULL END) AS max_package_lpa
        FROM companies c
        LEFT JOIN placements p ON c.company_id = p.company_id
        {where_clause}
        GROUP BY c.company_id
        ORDER BY total_offers DESC, c.company_name ASC;
    """

    with get_db_cursor(commit=False) as cursor:
        cursor.execute(query, params)
        return cursor.fetchall()

def get_company_by_id(company_id):
    """Retrieve details for a single company including placed students."""
    with get_db_cursor(commit=False) as cursor:
        cursor.execute("SELECT * FROM companies WHERE company_id = %s;", (company_id,))
        company = cursor.fetchone()
        if not company:
            return None

        # Fetch placements by this company
        cursor.execute("""
            SELECT p.*, s.student_name, s.roll_no, s.department, s.graduation_year
            FROM placements p
            JOIN students s ON p.student_id = s.student_id
            WHERE p.company_id = %s
            ORDER BY p.placement_date DESC;
        """, (company_id,))
        company["placements"] = cursor.fetchall()
        return company

def create_company(data):
    """Add a new recruiting company."""
    name = data.get("company_name", "").strip()
    industry = data.get("industry", "Information Technology").strip()
    location = data.get("location", "India").strip()
    website = data.get("website", "").strip() or None
    tier = data.get("tier", "Core / Product").strip()

    if not name:
        return False, "Company name is required."

    with get_db_cursor(commit=True) as cursor:
        cursor.execute("SELECT company_id FROM companies WHERE company_name = %s;", (name,))
        if cursor.fetchone():
            return False, f"A company named '{name}' already exists."

        cursor.execute("""
            INSERT INTO companies (company_name, industry, location, website, tier)
            VALUES (%s, %s, %s, %s, %s);
        """, (name, industry, location, website, tier))
        return True, cursor.lastrowid

def update_company(company_id, data):
    """Update company details."""
    name = data.get("company_name", "").strip()
    industry = data.get("industry", "Information Technology").strip()
    location = data.get("location", "India").strip()
    website = data.get("website", "").strip() or None
    tier = data.get("tier", "Core / Product").strip()

    if not name:
        return False, "Company name is required."

    with get_db_cursor(commit=True) as cursor:
        cursor.execute("SELECT company_id FROM companies WHERE company_name = %s AND company_id != %s;", (name, company_id))
        if cursor.fetchone():
            return False, f"Another company named '{name}' already exists."

        cursor.execute("""
            UPDATE companies
            SET company_name = %s, industry = %s, location = %s, website = %s, tier = %s
            WHERE company_id = %s;
        """, (name, industry, location, website, tier, company_id))
        return True, company_id

def delete_company(company_id):
    """Delete company and cascade placements."""
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("DELETE FROM companies WHERE company_id = %s;", (company_id,))
        return cursor.rowcount > 0

def get_all_industries():
    """Distinct industries for filter dropdowns."""
    with get_db_cursor(commit=False) as cursor:
        cursor.execute("SELECT DISTINCT industry FROM companies ORDER BY industry ASC;")
        return [r["industry"] for r in cursor.fetchall() if r["industry"]]
