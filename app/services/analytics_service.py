"""
Analytics Service Module.
Uses Pandas and NumPy for aggregations, placement rate formulas,
department cross-tabulations, salary distributions, and data-driven insights.
"""

import numpy as np
import pandas as pd

from app.database.connection import get_db_cursor


def load_placement_dataframe(department=None, graduation_year=None, company_id=None, status=None):
    """
    Fetch comprehensive student and placement records into a Pandas DataFrame.
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

    if company_id and str(company_id) != "All":
        try:
            conditions.append("p.company_id = %s")
            params.append(int(company_id))
        except ValueError:
            pass

    if status and status != "All":
        conditions.append("p.status = %s")
        params.append(status)

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

    query = f"""
        SELECT 
            s.student_id,
            s.roll_no,
            s.student_name,
            s.department,
            s.graduation_year,
            s.cgpa,
            s.gender,
            s.eligible_for_placement,
            p.placement_id,
            p.company_id,
            c.company_name,
            c.industry AS company_industry,
            c.tier AS company_tier,
            p.role,
            p.package_amount,
            p.package_unit,
            p.placement_date,
            p.placement_year,
            p.status AS placement_status,
            p.offer_type
        FROM students s
        LEFT JOIN placements p ON s.student_id = p.student_id
        LEFT JOIN companies c ON p.company_id = c.company_id
        {where_clause};
    """

    EXPECTED_COLUMNS = [
        "student_id",
        "roll_no",
        "student_name",
        "department",
        "graduation_year",
        "cgpa",
        "gender",
        "eligible_for_placement",
        "placement_id",
        "company_id",
        "company_name",
        "company_industry",
        "company_tier",
        "role",
        "package_amount",
        "package_unit",
        "placement_date",
        "placement_year",
        "placement_status",
        "offer_type",
    ]

    with get_db_cursor(commit=False) as cursor:
        cursor.execute(query, params)
        rows = cursor.fetchall()

    if not rows:
        return pd.DataFrame(columns=EXPECTED_COLUMNS)

    df = pd.DataFrame(rows)
    # Ensure proper data types
    df["cgpa"] = pd.to_numeric(df["cgpa"], errors="coerce")
    df["package_amount"] = pd.to_numeric(df["package_amount"], errors="coerce")
    df["eligible_for_placement"] = df["eligible_for_placement"].astype(int)
    return df


def get_kpis(department=None, graduation_year=None, company_id=None, status=None):
    """
    Calculate top-level placement performance metrics strictly adhering to definitions:
    - distinct eligible placed / total eligible * 100
    - unplaced = total eligible - distinct eligible placed
    """
    df = load_placement_dataframe(
        department=department, graduation_year=graduation_year, company_id=company_id, status=status
    )

    if df.empty:
        return {
            "total_students": 0,
            "total_eligible": 0,
            "total_placed": 0,
            "unplaced_students": 0,
            "placement_rate": 0.0,
            "avg_package": 0.0,
            "median_package": 0.0,
            "highest_package": 0.0,
            "lowest_package": 0.0,
            "total_companies": 0,
            "sample_label": "Synthetic Demonstration Data",
        }

    # Distinct students
    unique_students_df = df.drop_duplicates(subset=["student_id"])
    total_students = int(len(unique_students_df))

    # Eligible students
    eligible_students_df = unique_students_df[unique_students_df["eligible_for_placement"] == 1]
    total_eligible = int(len(eligible_students_df))

    # Placed students (only distinct eligible students who have a confirmed placed offer)
    placed_offers_df = df[
        (df["eligible_for_placement"] == 1)
        & (df["placement_status"].isin(["Placed", "Offer Accepted"]))
        & (df["package_amount"].notna())
    ]
    placed_student_ids = placed_offers_df["student_id"].unique()
    total_placed = int(len(placed_student_ids))

    # Unplaced eligible
    unplaced_students = max(0, total_eligible - total_placed)

    # Placement Rate Formula
    if total_eligible > 0:
        placement_rate = round((total_placed / total_eligible) * 100, 2)
    else:
        placement_rate = 0.0

    # Package statistics (from confirmed placed offers)
    valid_packages = placed_offers_df["package_amount"].dropna().values
    if len(valid_packages) > 0:
        avg_package = round(float(np.mean(valid_packages)), 2)
        median_package = round(float(np.median(valid_packages)), 2)
        highest_package = round(float(np.max(valid_packages)), 2)
        lowest_package = round(float(np.min(valid_packages)), 2)
    else:
        avg_package = 0.0
        median_package = 0.0
        highest_package = 0.0
        lowest_package = 0.0

    # Active companies with placements
    active_companies = placed_offers_df["company_id"].dropna().unique()
    total_companies = int(len(active_companies))

    return {
        "total_students": total_students,
        "total_eligible": total_eligible,
        "total_placed": total_placed,
        "unplaced_students": unplaced_students,
        "placement_rate": placement_rate,
        "avg_package": avg_package,
        "median_package": median_package,
        "highest_package": highest_package,
        "lowest_package": lowest_package,
        "total_companies": total_companies,
        "sample_label": "Synthetic Demonstration Data",
    }


def get_department_analytics(graduation_year=None):
    """
    Calculate department-wise comparison metrics using Pandas.
    """
    df = load_placement_dataframe(graduation_year=graduation_year)
    if df.empty:
        return []

    dept_records = []
    departments = sorted(df["department"].dropna().unique())

    for dept in departments:
        dept_df = df[df["department"] == dept]
        dept_unique = dept_df.drop_duplicates(subset=["student_id"])

        total_students = int(len(dept_unique))
        eligible_df = dept_unique[dept_unique["eligible_for_placement"] == 1]
        eligible_count = int(len(eligible_df))

        placed_offers = dept_df[
            (dept_df["eligible_for_placement"] == 1)
            & (dept_df["placement_status"].isin(["Placed", "Offer Accepted"]))
            & (dept_df["package_amount"].notna())
        ]
        placed_students_count = int(len(placed_offers["student_id"].unique()))
        unplaced_count = max(0, eligible_count - placed_students_count)

        rate = round((placed_students_count / eligible_count) * 100, 2) if eligible_count > 0 else 0.0

        packages = placed_offers["package_amount"].dropna().values
        avg_pkg = round(float(np.mean(packages)), 2) if len(packages) > 0 else 0.0
        med_pkg = round(float(np.median(packages)), 2) if len(packages) > 0 else 0.0
        max_pkg = round(float(np.max(packages)), 2) if len(packages) > 0 else 0.0

        dept_records.append(
            {
                "department": dept,
                "total_students": total_students,
                "eligible_students": eligible_count,
                "placed_students": placed_students_count,
                "unplaced_students": unplaced_count,
                "placement_rate": rate,
                "avg_package": avg_pkg,
                "median_package": med_pkg,
                "highest_package": max_pkg,
            }
        )

    # Sort descending by placement rate
    dept_records.sort(key=lambda x: x["placement_rate"], reverse=True)
    return dept_records


def get_package_analytics(department=None, graduation_year=None):
    """
    Calculate salary package distributions, percentiles, tiers, and top offers.
    """
    df = load_placement_dataframe(department=department, graduation_year=graduation_year)
    placed_offers = df[(df["placement_status"].isin(["Placed", "Offer Accepted"])) & (df["package_amount"].notna())]

    packages = placed_offers["package_amount"].values
    if len(packages) == 0:
        return {
            "count": 0,
            "mean": 0.0,
            "median": 0.0,
            "std": 0.0,
            "min": 0.0,
            "max": 0.0,
            "p25": 0.0,
            "p75": 0.0,
            "p90": 0.0,
            "brackets": {},
            "top_offers": [],
        }

    stats = {
        "count": int(len(packages)),
        "mean": round(float(np.mean(packages)), 2),
        "median": round(float(np.median(packages)), 2),
        "std": round(float(np.std(packages)), 2),
        "min": round(float(np.min(packages)), 2),
        "max": round(float(np.max(packages)), 2),
        "p25": round(float(np.percentile(packages, 25)), 2),
        "p75": round(float(np.percentile(packages, 75)), 2),
        "p90": round(float(np.percentile(packages, 90)), 2),
    }

    # Bracket categorization
    b_less_5 = int(np.sum(packages < 5.0))
    b_5_to_8 = int(np.sum((packages >= 5.0) & (packages < 8.0)))
    b_8_to_15 = int(np.sum((packages >= 8.0) & (packages < 15.0)))
    b_above_15 = int(np.sum(packages >= 15.0))

    stats["brackets"] = {
        "less_than_5": {
            "label": "< 5 LPA (Mass / Entry)",
            "count": b_less_5,
            "pct": round(b_less_5 / len(packages) * 100, 1),
        },
        "5_to_8": {
            "label": "5 - 8 LPA (Standard / Core)",
            "count": b_5_to_8,
            "pct": round(b_5_to_8 / len(packages) * 100, 1),
        },
        "8_to_15": {
            "label": "8 - 15 LPA (Dream Offers)",
            "count": b_8_to_15,
            "pct": round(b_8_to_15 / len(packages) * 100, 1),
        },
        "above_15": {
            "label": "Above 15 LPA (Super Dream)",
            "count": b_above_15,
            "pct": round(b_above_15 / len(packages) * 100, 1),
        },
    }

    # Top offers
    top_df = placed_offers.sort_values(by="package_amount", ascending=False).head(10)
    top_offers = []
    for _, row in top_df.iterrows():
        top_offers.append(
            {
                "student_name": row["student_name"],
                "roll_no": row["roll_no"],
                "department": row["department"],
                "company_name": row["company_name"],
                "role": row["role"],
                "package_amount": row["package_amount"],
                "tier": row["company_tier"],
            }
        )
    stats["top_offers"] = top_offers

    return stats


def get_skill_analytics(department=None):
    """
    Skill frequency among placed vs unplaced students.
    """
    dept_condition = "WHERE s.department = %s" if department and department != "All" else ""
    params = [department] if department and department != "All" else []

    query = f"""
        SELECT 
            sk.skill_name,
            sk.skill_category,
            COUNT(DISTINCT ss.student_id) AS total_students_with_skill,
            COUNT(DISTINCT CASE WHEN p.status IN ('Placed', 'Offer Accepted') THEN ss.student_id END) AS placed_students_with_skill,
            COUNT(DISTINCT CASE WHEN s.eligible_for_placement = 1 AND (p.status IS NULL OR p.status NOT IN ('Placed', 'Offer Accepted')) THEN ss.student_id END) AS unplaced_students_with_skill
        FROM skills sk
        JOIN student_skills ss ON sk.skill_id = ss.skill_id
        JOIN students s ON ss.student_id = s.student_id
        LEFT JOIN placements p ON s.student_id = p.student_id
        {dept_condition}
        GROUP BY sk.skill_id
        ORDER BY placed_students_with_skill DESC, total_students_with_skill DESC;
    """

    with get_db_cursor(commit=False) as cursor:
        cursor.execute(query, params)
        rows = cursor.fetchall()
    return rows


def get_yearly_trends():
    """
    Yearly progression of placements and package metrics across graduation years.
    """
    query = """
        SELECT 
            s.graduation_year,
            COUNT(DISTINCT s.student_id) AS total_students,
            COUNT(DISTINCT CASE WHEN s.eligible_for_placement = 1 THEN s.student_id END) AS eligible_students,
            COUNT(DISTINCT CASE WHEN s.eligible_for_placement = 1 AND p.status IN ('Placed', 'Offer Accepted') THEN s.student_id END) AS placed_students,
            ROUND(AVG(CASE WHEN p.status IN ('Placed', 'Offer Accepted') THEN p.package_amount END), 2) AS avg_package_lpa,
            MAX(CASE WHEN p.status IN ('Placed', 'Offer Accepted') THEN p.package_amount END) AS max_package_lpa
        FROM students s
        LEFT JOIN placements p ON s.student_id = p.student_id
        WHERE s.graduation_year IS NOT NULL
        GROUP BY s.graduation_year
        ORDER BY s.graduation_year ASC;
    """
    with get_db_cursor(commit=False) as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    for r in rows:
        eligible = r["eligible_students"] or 0
        placed = r["placed_students"] or 0
        r["placement_rate"] = round((placed / eligible) * 100, 2) if eligible > 0 else 0.0
        r["unplaced_students"] = max(0, eligible - placed)

    return rows


def generate_placement_insights(department=None, graduation_year=None):
    """
    Generate dynamic, factual observations derived strictly from filtered database records.
    """
    kpis = get_kpis(department=department, graduation_year=graduation_year)
    depts = get_department_analytics(graduation_year=graduation_year)
    skills = get_skill_analytics(department=department)
    pkg = get_package_analytics(department=department, graduation_year=graduation_year)

    insights = []

    # 1. Overall placement rate insight
    if kpis["total_eligible"] > 0:
        insights.append(
            f"Overall placement rate stands at **{kpis['placement_rate']}%**, with **{kpis['total_placed']}** out of **{kpis['total_eligible']}** eligible candidates successfully placed."
        )

    # 2. Leading department insight
    if depts:
        best_dept = depts[0]
        insights.append(
            f"**{best_dept['department']}** recorded the highest placement rate at **{best_dept['placement_rate']}%** ({best_dept['placed_students']}/{best_dept['eligible_students']} eligible placed) with an average CTC of **{best_dept['avg_package']} LPA**."
        )

    # 3. Package insight
    if pkg["count"] > 0:
        insights.append(
            f"The salary package spans from **{pkg['min']} LPA** up to a peak super-dream offer of **{pkg['max']} LPA**, with median CTC recorded at **{pkg['median']} LPA**."
        )
        super_dream_pct = pkg["brackets"]["above_15"]["pct"]
        insights.append(
            f"**{super_dream_pct}%** of all confirmed placements secured Super Dream packages exceeding **15 LPA**."
        )

    # 4. In-demand skills insight
    if skills:
        top_skills = [s["skill_name"] for s in skills[:3]]
        insights.append(
            f"The top technical skills most recorded among placed candidates are **{', '.join(top_skills)}**."
        )

    # 5. Unplaced students focus
    if kpis["unplaced_students"] > 0:
        insights.append(
            f"**{kpis['unplaced_students']}** eligible students currently require additional placement assistance and interview preparation."
        )

    return insights
