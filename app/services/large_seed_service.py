"""
Large Synthetic Benchmark Dataset Generator.
Generates 600 realistic student academic and recruitment records with authentic
distributions for machine learning training, cross-validation, and benchmarking.
All generated records are clearly labelled as synthetic.
"""

import random

import numpy as np

from app.database.connection import get_db_cursor

FIRST_NAMES = [
    "Aarav",
    "Aditi",
    "Aditya",
    "Akash",
    "Ananya",
    "Aniket",
    "Ankita",
    "Arjun",
    "Bhavya",
    "Chetan",
    "Deepika",
    "Dev",
    "Divya",
    "Gaurav",
    "Harsh",
    "Isha",
    "Karan",
    "Kavya",
    "Madhav",
    "Manish",
    "Meera",
    "Neha",
    "Nikhil",
    "Nisha",
    "Pooja",
    "Pranav",
    "Priya",
    "Rahul",
    "Rhea",
    "Rishi",
    "Rohan",
    "Sahil",
    "Sakshi",
    "Sanjay",
    "Shreya",
    "Siddharth",
    "Sneha",
    "Tarun",
    "Varun",
    "Vikas",
]

LAST_NAMES = [
    "Sharma",
    "Verma",
    "Gupta",
    "Patel",
    "Reddy",
    "Nair",
    "Iyer",
    "Rao",
    "Kumar",
    "Singh",
    "Joshi",
    "Bose",
    "Mehta",
    "Chopra",
    "Kulkarni",
    "Deshmukh",
    "Mishra",
    "Pandey",
    "Agarwal",
    "Bhatia",
    "Saxena",
    "Das",
    "Menon",
    "Pillai",
]

DEPARTMENTS = [
    ("Computer Science and Engineering", "BCE", 180),
    ("Artificial Intelligence and Machine Learning", "AML", 150),
    ("Information Technology", "BIT", 100),
    ("Electronics and Communication Engineering", "ECE", 90),
    ("Electrical and Electronics Engineering", "EEE", 40),
    ("Mechanical Engineering", "MEC", 40),
]

ROLES_BY_TIER = {
    "Super Dream": [
        "Software Development Engineer II",
        "AI Research Engineer",
        "Systems Architect",
        "Machine Learning Engineer",
    ],
    "Dream": ["Full-Stack Software Engineer", "Data Engineer", "Cloud Associate", "DevOps Engineer"],
    "Core Engineering": ["Embedded Systems Engineer", "Robotics Firmware Engineer", "Control Systems Associate"],
    "Mass Recruit": ["Systems Engineer", "Associate Software Consultant", "Application Developer"],
}


def generate_large_synthetic_dataset(target_count=600):
    """
    Generate and insert authentic synthetic student records, verified skills,
    and placement offer histories.
    """
    np.random.seed(42)
    random.seed(42)

    with get_db_cursor(commit=False) as cursor:
        # Load available skills and companies
        cursor.execute("SELECT skill_id, skill_name, skill_category FROM skills;")
        skills_db = cursor.fetchall()

        cursor.execute("SELECT company_id, company_name, tier FROM companies;")
        companies_db = cursor.fetchall()

    if not skills_db or not companies_db:
        return False, "Base master records (skills and companies) must exist before generating large synthetic seed."

    skills_by_name = {s["skill_name"]: s["skill_id"] for s in skills_db}
    companies_by_tier = {}
    for c in companies_db:
        tier = c["tier"] or "Mass Recruit"
        companies_by_tier.setdefault(tier, []).append(c)

    students_to_insert = []

    roll_counter = 2000
    total_generated = 0

    for dept_name, code, count in DEPARTMENTS:
        for _ in range(count):
            roll_counter += 1
            roll_no = f"22{code}{roll_counter}"
            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)
            full_name = f"{first} {last}"
            gender = random.choice(["Male", "Female"])
            email = f"{first.lower()}.{last.lower()}{roll_counter % 1000}@college.edu"
            phone = f"98{random.randint(10000000, 99999999)}"
            grad_year = random.choice([2024, 2025, 2026, 2026, 2026, 2027])

            # Realistic CGPA distribution
            cgpa = float(np.clip(np.random.normal(7.85, 0.82), 5.50, 9.92))
            cgpa = round(cgpa, 2)

            # Eligibility rule
            eligible = 1 if (cgpa >= 6.25 and random.random() > 0.05) else 0

            students_to_insert.append(
                {
                    "roll_no": roll_no,
                    "student_name": full_name,
                    "department": dept_name,
                    "graduation_year": grad_year,
                    "cgpa": cgpa,
                    "email": email,
                    "phone": phone,
                    "gender": gender,
                    "eligible": eligible,
                    "temp_id": total_generated,
                }
            )
            total_generated += 1

    # Insert students into database
    created_student_ids = []
    with get_db_cursor(commit=True) as cursor:
        for st in students_to_insert:
            cursor.execute(
                """
                INSERT INTO students 
                (roll_no, student_name, department, graduation_year, cgpa, email, phone, gender, eligible_for_placement)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE student_name = VALUES(student_name), cgpa = VALUES(cgpa);
                """,
                (
                    st["roll_no"],
                    st["student_name"],
                    st["department"],
                    st["graduation_year"],
                    st["cgpa"],
                    st["email"],
                    st["phone"],
                    st["gender"],
                    st["eligible"],
                ),
            )
            created_student_ids.append((cursor.lastrowid or 0, st))

    # Fetch inserted student records with their auto-increment IDs
    with get_db_cursor(commit=False) as cursor:
        cursor.execute(
            "SELECT student_id, roll_no, department, cgpa, eligible_for_placement FROM students WHERE roll_no LIKE '22%';"
        )
        persisted_students = cursor.fetchall()

    # Skill assignment and placement offer determination
    placement_rows = []
    skill_rows = []

    for st in persisted_students:
        sid = st["student_id"]
        cgpa = float(st["cgpa"] or 7.0)
        eligible = int(st["eligible_for_placement"] or 0)
        dept = st["department"]

        # Assign relevant skills based on branch
        dept_relevant_skills = ["Communication Skills", "Problem Solving"]
        if "Computer" in dept or "Artificial" in dept or "Information" in dept:
            dept_relevant_skills += ["Python", "SQL", "Data Structures & Algorithms", "C++"]
            if cgpa >= 7.8:
                dept_relevant_skills += ["Machine Learning", "React.js", "Docker & Kubernetes", "FastAPI"]
            if cgpa >= 8.5:
                dept_relevant_skills += ["Deep Learning", "Natural Language Processing", "Distributed Systems"]
        elif "Electronics" in dept:
            dept_relevant_skills += ["Embedded Systems", "IoT Protocols", "C++", "Python", "Verilog / VHDL"]
        elif "Electrical" in dept:
            dept_relevant_skills += ["MATLAB / Simulink", "Power Systems Analysis", "Python", "PLC Programming"]
        else:
            dept_relevant_skills += ["AutoCAD", "SolidWorks", "Finite Element Analysis", "Python"]

        # Sample 3 to 7 verified skills
        chosen_skills = random.sample(dept_relevant_skills, min(len(dept_relevant_skills), random.randint(3, 6)))
        for sname in chosen_skills:
            if sname in skills_by_name:
                skill_rows.append((sid, skills_by_name[sname]))

        # Placement Probability Model
        has_dsa = 1 if "Data Structures & Algorithms" in chosen_skills else 0
        has_python = 1 if "Python" in chosen_skills else 0
        has_aiml = 1 if "Machine Learning" in chosen_skills or "Deep Learning" in chosen_skills else 0

        if eligible:
            skill_bonus = (has_dsa * 0.22) + (has_python * 0.15) + (has_aiml * 0.15)
            gpa_factor = (cgpa - 6.2) / 3.6
            prob = 0.15 + gpa_factor * 0.55 + skill_bonus
            jitter = random.uniform(-0.06, 0.06)
            is_placed = (prob + jitter) >= 0.55
        else:
            is_placed = False

        if is_placed:
            # Determine Tier based on CGPA and advanced skill density
            if cgpa >= 8.6 and (has_dsa and (has_aiml or has_python)):
                tier = "Super Dream"
                pkg = round(float(np.clip(np.random.normal(24.5, 6.0), 16.0, 48.0)), 2)
            elif cgpa >= 7.5:
                tier = "Dream"
                pkg = round(float(np.clip(np.random.normal(11.5, 2.2), 8.0, 16.0)), 2)
            else:
                tier = "Mass Recruit"
                pkg = round(float(np.clip(np.random.normal(5.2, 1.2), 3.6, 7.8)), 2)

            comp_pool = companies_by_tier.get(tier) or companies_by_tier.get("Mass Recruit", companies_db)
            comp = random.choice(comp_pool)
            role = random.choice(ROLES_BY_TIER.get(tier, ["Software Engineer"]))
            status = "Placed"
            placement_date = f"2025-{random.randint(9, 12):02d}-{random.randint(1, 28):02d}"

            placement_rows.append(
                (
                    sid,
                    comp["company_id"],
                    role,
                    pkg,
                    "LPA",
                    placement_date,
                    2026,
                    status,
                    tier,
                    "Synthetic Benchmark Dataset",
                )
            )

    # Bulk insert skills and placements
    with get_db_cursor(commit=True) as cursor:
        if skill_rows:
            cursor.executemany("INSERT IGNORE INTO student_skills (student_id, skill_id) VALUES (%s, %s);", skill_rows)
        if placement_rows:
            cursor.execute("DELETE FROM placements WHERE notes = 'Synthetic Benchmark Dataset';")
            cursor.executemany(
                """
                INSERT INTO placements 
                (student_id, company_id, role, package_amount, package_unit, placement_date, placement_year, status, offer_type, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """,
                placement_rows,
            )

    return (
        True,
        f"Successfully populated {len(persisted_students)} synthetic student profiles and {len(placement_rows)} placement records.",
    )
