"""
Smart Skill Gap & Career Pathway Recommender Service.
Analyzes student skill inventories against target recruiter requirements,
computes match scores, isolates critical skill gaps, and generates learning roadmaps.
"""
from app.database.connection import get_db_cursor
from app.services.student_service import get_student_by_id
from app.services.company_service import get_company_by_id

# Benchmark skill profiles by hiring tiers (derived from campus drive standards)
TIER_PROFILES = {
    "Super Dream": {
        "title": "Super Dream Companies (> 15 LPA CTC)",
        "description": "High-package product engineering roles (e.g. Google, Microsoft, Amazon, NVIDIA, Qualcomm).",
        "benchmark_ctc": "25.0 LPA",
        "core_skills": [
            {"skill_name": "Data Structures & Algorithms", "category": "Core CS", "priority": "Critical", "weight": 25},
            {"skill_name": "Python", "category": "Programming", "priority": "High", "weight": 20},
            {"skill_name": "SQL", "category": "Database & Querying", "priority": "High", "weight": 15},
            {"skill_name": "Machine Learning", "category": "AI/Data Science", "priority": "High", "weight": 15},
            {"skill_name": "Cloud Computing (AWS/GCP)", "category": "DevOps & Cloud", "priority": "Medium", "weight": 15},
            {"skill_name": "Problem Solving", "category": "Aptitude & Soft Skills", "priority": "High", "weight": 10}
        ]
    },
    "Dream": {
        "title": "Dream Companies (8 - 15 LPA CTC)",
        "description": "Specialized technology consulting & digital firms (e.g. Cisco, Oracle, Deloitte, Accenture).",
        "benchmark_ctc": "11.5 LPA",
        "core_skills": [
            {"skill_name": "SQL", "category": "Database & Querying", "priority": "Critical", "weight": 25},
            {"skill_name": "Python", "category": "Programming", "priority": "High", "weight": 20},
            {"skill_name": "Data Structures & Algorithms", "category": "Core CS", "priority": "High", "weight": 20},
            {"skill_name": "React.js", "category": "Web Development", "priority": "Medium", "weight": 15},
            {"skill_name": "Communication Skills", "category": "Aptitude & Soft Skills", "priority": "High", "weight": 10},
            {"skill_name": "Problem Solving", "category": "Aptitude & Soft Skills", "priority": "Medium", "weight": 10}
        ]
    },
    "Core Engineering": {
        "title": "Core Engineering Companies (6 - 12 LPA CTC)",
        "description": "Hardware, automotive, IoT, and embedded innovators (e.g. Bosch, Tata Motors, L&T).",
        "benchmark_ctc": "8.5 LPA",
        "core_skills": [
            {"skill_name": "Embedded Systems", "category": "Core Engineering", "priority": "Critical", "weight": 25},
            {"skill_name": "IoT & Microcontrollers", "category": "Core Engineering", "priority": "Critical", "weight": 25},
            {"skill_name": "C++", "category": "Programming", "priority": "High", "weight": 20},
            {"skill_name": "Python", "category": "Programming", "priority": "Medium", "weight": 15},
            {"skill_name": "Problem Solving", "category": "Aptitude & Soft Skills", "priority": "High", "weight": 15}
        ]
    },
    "Mass / IT Services": {
        "title": "Mass Recruitment & IT Services (3.5 - 7 LPA CTC)",
        "description": "Large-scale IT solution providers (e.g. TCS, Infosys, Wipro, Cognizant).",
        "benchmark_ctc": "4.5 LPA",
        "core_skills": [
            {"skill_name": "SQL", "category": "Database & Querying", "priority": "Critical", "weight": 25},
            {"skill_name": "Python", "category": "Programming", "priority": "High", "weight": 25},
            {"skill_name": "Communication Skills", "category": "Aptitude & Soft Skills", "priority": "Critical", "weight": 25},
            {"skill_name": "HTML/CSS/JavaScript", "category": "Web Development", "priority": "Medium", "weight": 15},
            {"skill_name": "Problem Solving", "category": "Aptitude & Soft Skills", "priority": "Medium", "weight": 10}
        ]
    }
}

def get_target_skills_for_company(company_id):
    """
    Extract skills most frequently associated with students placed at a specific company.
    Fallback to tier benchmark if few specific records exist.
    """
    company = get_company_by_id(company_id)
    if not company:
        return []

    query = """
        SELECT sk.skill_name, sk.skill_category, COUNT(DISTINCT s.student_id) as hire_count
        FROM placements p
        JOIN students s ON p.student_id = s.student_id
        JOIN student_skills ss ON s.student_id = ss.student_id
        JOIN skills sk ON ss.skill_id = sk.skill_id
        WHERE p.company_id = %s AND p.status IN ('Placed', 'Offer Accepted')
        GROUP BY sk.skill_id
        ORDER BY hire_count DESC
        LIMIT 6;
    """
    with get_db_cursor(commit=False) as cursor:
        cursor.execute(query, (company_id,))
        rows = cursor.fetchall()

    if rows and len(rows) >= 3:
        skills_res = []
        for r in rows:
            skills_res.append({
                "skill_name": r["skill_name"],
                "category": r["skill_category"],
                "priority": "Critical" if r["hire_count"] >= 3 else "High",
                "weight": 20
            })
        return skills_res

    # Fallback to tier profile
    tier = company.get("tier", "Dream")
    profile = TIER_PROFILES.get(tier, TIER_PROFILES["Dream"])
    return profile["core_skills"]

def analyze_skill_gap(current_skills_list, target_type="tier", target_value="Super Dream"):
    """
    Perform deep gap analysis between candidate skills and target requirement.
    Returns: match score %, acquired skills, missing skills, readiness tier, and learning roadmap.
    """
    current_skills_set = {s.strip().lower() for s in (current_skills_list or [])}

    if target_type == "company":
        try:
            cid = int(target_value)
            company = get_company_by_id(cid)
            target_title = company["company_name"] if company else "Company Target"
            target_skills = get_target_skills_for_company(cid)
            target_desc = f"Based on verified hiring data from {target_title} campus drives."
        except (ValueError, TypeError):
            target_title = "Company Target"
            target_skills = TIER_PROFILES["Super Dream"]["core_skills"]
            target_desc = "Standard recruitment benchmark."
    else:
        profile = TIER_PROFILES.get(target_value, TIER_PROFILES["Super Dream"])
        target_title = profile["title"]
        target_skills = profile["core_skills"]
        target_desc = profile["description"]

    acquired = []
    missing = []
    total_weight = 0
    acquired_weight = 0

    for req in target_skills:
        req_name = req["skill_name"]
        w = req.get("weight", 20)
        total_weight += w

        if req_name.strip().lower() in current_skills_set:
            acquired.append(req)
            acquired_weight += w
        else:
            missing.append(req)

    # Compute weighted match score
    match_score = round((acquired_weight / total_weight) * 100, 1) if total_weight > 0 else 0.0

    # Readiness Tier
    if match_score >= 80.0:
        readiness = "Drive Ready (High Candidate Affinity)"
        badge_class = "badge-placed"
        advice = "Candidate matches primary technical screening criteria for this target. Recommended to proceed directly to mock coding assessments and system design rounds."
    elif match_score >= 50.0:
        readiness = "Moderate Gap (Achievable in 3–5 Weeks)"
        badge_class = "badge-pending"
        advice = "Candidate demonstrates solid foundational capabilities. Bridging 1 or 2 specific gaps will unlock high-confidence shortlisting."
    else:
        readiness = "Significant Skill Gap (Remedial Action Required)"
        badge_class = "badge-rejected"
        advice = "Candidate currently lacks multiple core competencies demanded by this recruiter tier. Structured coaching and project development recommended."

    # Generate Learning Roadmap (3 Structured Phases)
    phase1_skills = [m["skill_name"] for m in missing if m.get("priority") == "Critical"]
    phase2_skills = [m["skill_name"] for m in missing if m.get("priority") != "Critical"]

    roadmap = [
        {
            "phase": "Phase 1: Foundational Core Mastery (Weeks 1-2)",
            "focus": f"Master critical missing prerequisites: {', '.join(phase1_skills) if phase1_skills else 'Reinforce Data Structures & Problem Solving speed'}.",
            "action": "Complete daily LeetCode/HackerRank challenges and verify conceptual depth."
        },
        {
            "phase": "Phase 2: Project Implementation & GitHub Proof (Weeks 3-4)",
            "focus": f"Build practical capstone projects incorporating: {', '.join(phase2_skills) if phase2_skills else 'Full-Stack / Machine Learning architectures'}.",
            "action": "Deploy live web applications and document README architecture on GitHub."
        },
        {
            "phase": "Phase 3: Mock Recruitment & Interview Polish (Weeks 5-6)",
            "focus": "Simulate technical coding rounds, aptitude tests, and behavioral HR interviews.",
            "action": "Schedule 2 mock technical evaluations with department placement coordinators."
        }
    ]

    return {
        "target_title": target_title,
        "target_desc": target_desc,
        "match_score": match_score,
        "readiness": readiness,
        "badge_class": badge_class,
        "advice": advice,
        "acquired_skills": acquired,
        "missing_skills": missing,
        "total_required": len(target_skills),
        "roadmap": roadmap
    }

def analyze_student_skill_gap(student_id, target_type="tier", target_value="Super Dream"):
    """Run skill gap analysis for an existing registered student."""
    student = get_student_by_id(student_id)
    if not student:
        return None

    skills_names = [s["skill_name"] for s in student.get("skills", [])]
    analysis = analyze_skill_gap(skills_names, target_type=target_type, target_value=target_value)
    analysis["student"] = student
    return analysis
