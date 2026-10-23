"""
Natural Language Processing (NLP) ATS Resume & Job Description Matcher Service.
Computes TF-IDF vector similarity, cosine alignment, keyword extraction,
and actionable ATS optimization recommendations.
"""
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.services.student_service import get_student_by_id

# Curated Technical & Core Competencies Taxonomy for keyword extraction
TECH_KEYWORDS = [
    # Languages
    "python", "java", "c++", "c#", "c", "javascript", "typescript", "html", "css", "sql", "r", "go",
    # Frameworks & Web
    "react", "react.js", "angular", "vue", "node.js", "django", "flask", "fastapi", "spring boot", "bootstrap",
    # AI / ML & Data Science
    "machine learning", "deep learning", "natural language processing", "nlp", "computer vision",
    "data science", "data analysis", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch",
    "artificial intelligence", "generative ai", "neural networks",
    # Databases & Storage
    "mysql", "postgresql", "mongodb", "redis", "oracle", "database", "nosql", "query optimization",
    # Cloud & DevOps
    "aws", "amazon web services", "azure", "gcp", "google cloud", "docker", "kubernetes", "git",
    "github", "ci/cd", "linux", "rest api", "microservices", "cloud computing",
    # Core CS & Professional
    "data structures", "algorithms", "dsa", "object oriented programming", "oop", "system design",
    "problem solving", "communication skills", "agile", "scrum", "unit testing", "debugging"
]

# Preloaded Benchmark Job Descriptions for campus drives
SAMPLE_JOB_DESCRIPTIONS = {
    "google_swe": {
        "title": "Google — Software Engineer (Campus Graduate)",
        "company": "Google",
        "tier": "Super Dream",
        "text": """Google is looking for Software Engineers to build large-scale distributed systems and high-impact consumer applications.
Requirements:
- Bachelor's degree in Computer Science, AI/ML, or related technical field.
- Proficiency in Python, C++, or Java with solid Object-Oriented Programming (OOP) design principles.
- Strong foundation in Data Structures and Algorithms (DSA), time-space complexity, and problem solving.
- Familiarity with Cloud Computing (Google Cloud Platform / GCP), REST API design, and distributed databases (SQL, NoSQL).
- Experience with Git version control, unit testing, CI/CD pipelines, and Linux environments.
- Excellent analytical, communication skills, and collaborative team mindset."""
    },
    "amazon_sde": {
        "title": "Amazon — Software Development Engineer I (SDE-1)",
        "company": "Amazon",
        "tier": "Super Dream",
        "text": """Amazon is hiring SDE-1 candidates for our AWS and Consumer Technology teams.
Key Responsibilities & Qualifications:
- Degree in B.Tech Computer Science, Information Technology, or Artificial Intelligence.
- Strong coding competency in Java, Python, or C++.
- Proven command of Data Structures, Algorithms, dynamic programming, and systems architecture.
- Experience building scalable web applications and REST APIs using AWS (Amazon Web Services), Lambda, S3, or DynamoDB.
- Practical knowledge of SQL relational databases, MySQL, query optimization, and NoSQL storage.
- Passion for customer obsession, clean code, automated testing, and agile scrum delivery."""
    },
    "microsoft_ai": {
        "title": "Microsoft — Cloud & AI Software Engineer",
        "company": "Microsoft",
        "tier": "Super Dream",
        "text": """Join Microsoft to empower every person and organization on the planet. We are hiring Cloud & AI Engineers.
Qualifications:
- Solid programming experience in Python, C#, or Java.
- Hands-on experience with Machine Learning, Deep Learning, Natural Language Processing (NLP), or Computer Vision.
- Familiarity with Azure cloud computing, Docker containers, Kubernetes, and microservices architecture.
- Working knowledge of SQL, database modeling, and Git collaboration workflows.
- Strong mathematical reasoning, problem solving, and verbal communication skills."""
    },
    "tcs_digital": {
        "title": "TCS — Digital Specialist Programmer",
        "company": "Tata Consultancy Services",
        "tier": "Dream / Digital",
        "text": """TCS Digital hiring for high-growth software and digital transformation tracks.
Job Description:
- Proficiency in Python, Java, JavaScript, HTML, and CSS.
- Hands-on web development with React.js, Flask, Django, or Spring Boot.
- Relational database management using MySQL or SQL Server.
- Understanding of Data Structures, Algorithms, and logical problem solving.
- Familiarity with version control (Git/GitHub), Agile methodologies, and software unit testing.
- Strong aptitude, communication skills, and fast learning agility."""
    },
    "deloitte_analyst": {
        "title": "Deloitte — Technology & Data Analyst",
        "company": "Deloitte",
        "tier": "Dream",
        "text": """Deloitte is seeking dynamic Technology and Data Analysts to advise Fortune 500 clients.
Role Requirements:
- Strong analytical skills with proficiency in Python, SQL, and Data Analysis.
- Familiarity with Machine Learning, statistics, Pandas, NumPy, and Scikit-Learn.
- Experience creating dashboards and reporting insights using SQL databases.
- Exceptional written and verbal communication skills, client presentation, and business problem solving.
- Ability to work effectively in cross-functional agile teams."""
    }
}

def clean_text(text):
    """Normalize text: lowercase, replace hyphens/slashes with spaces, remove punctuation, collapse whitespace."""
    if not text:
        return ""
    text = text.lower()
    text = text.replace("-", " ").replace("/", " ")
    text = re.sub(r"[^\w\s\+\#\.]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def extract_keywords(text):
    """Isolate matched technical and domain competencies from text using ontology lookup."""
    cleaned = clean_text(text)
    matched = set()
    for kw in TECH_KEYWORDS:
        # Check whole word match or phrase match
        pattern = r"\b" + re.escape(kw) + r"\b"
        if re.search(pattern, cleaned):
            matched.add(kw)
    return matched

def calculate_ats_match(resume_text, job_description_text):
    """
    Computes NLP ATS match between candidate resume and job description.
    Returns:
      - ats_score_pct (0-100%)
      - cosine_similarity_pct
      - keyword_coverage_pct
      - matched_keywords
      - missing_keywords
      - readiness_status
      - recommendations
    """
    cleaned_resume = clean_text(resume_text)
    cleaned_jd = clean_text(job_description_text)

    if not cleaned_resume or not cleaned_jd:
        return {
            "ats_score": 0.0,
            "cosine_sim": 0.0,
            "keyword_coverage": 0.0,
            "matched_keywords": [],
            "missing_keywords": [],
            "readiness": "Input Required",
            "badge_class": "badge-rejected",
            "advice": "Please provide both candidate resume text and recruiter job description."
        }

    # 1. TF-IDF & Cosine Similarity
    try:
        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=2500
        )
        tfidf_matrix = vectorizer.fit_transform([cleaned_resume, cleaned_jd])
        cosine_sim = float(cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0])
        cosine_pct = round(max(0.0, min(1.0, cosine_sim)) * 100, 1)
    except Exception:
        cosine_pct = 0.0

    # 2. Keyword Matching & Coverage
    resume_kws = extract_keywords(cleaned_resume)
    jd_kws = extract_keywords(cleaned_jd)

    matched = sorted(list(resume_kws.intersection(jd_kws)))
    missing = sorted(list(jd_kws - resume_kws))

    total_jd_keywords = len(jd_kws)
    if total_jd_keywords > 0:
        keyword_coverage = round((len(matched) / total_jd_keywords) * 100, 1)
    else:
        keyword_coverage = cosine_pct

    # 3. Blended Composite ATS Score
    # Keyword coverage carries 60% weight, semantic TF-IDF cosine similarity carries 40%
    # We apply a slight realistic calibration so good matches achieve 75-90%
    raw_ats = (0.60 * keyword_coverage) + (0.40 * (cosine_pct * 1.5))
    ats_score = round(max(5.0, min(98.0, raw_ats)), 1)

    # 4. Status and Recommendations
    if ats_score >= 75.0:
        readiness = "High ATS Shortlist Probability"
        badge_class = "badge-placed"
        advice = "Candidate resume closely aligns with recruiter technical requirements. Highly likely to pass automated ATS screening filters."
    elif ats_score >= 50.0:
        readiness = "Moderate ATS Compatibility"
        badge_class = "badge-pending"
        advice = "Candidate matches primary competencies, but missing critical secondary keywords may lower ranking in large applicant pools."
    else:
        readiness = "Low ATS Compatibility (High Rejection Risk)"
        badge_class = "badge-rejected"
        advice = "Significant disparity between candidate resume and job description. Incorporate the identified missing competencies before applying."

    # 5. Tailored Optimization Recommendations
    recommendations = []
    if missing:
        top_missing = missing[:5]
        recommendations.append(f"Incorporate missing core keywords into your Experience & Project descriptions: {', '.join([k.title() for k in top_missing])}.")
    if cosine_pct < 25.0:
        recommendations.append("Align project descriptions with the exact industry phrasing used in the job description.")
    recommendations.append("Ensure your technical skills section uses standard industry terms (e.g., 'REST API', 'MySQL', 'Git').")
    recommendations.append("Quantify project outcomes with concrete numerical results (e.g., 'Optimized query latency by 35%').")

    return {
        "ats_score": ats_score,
        "cosine_sim": cosine_pct,
        "keyword_coverage": keyword_coverage,
        "matched_keywords": [k.title() for k in matched],
        "missing_keywords": [k.title() for k in missing],
        "total_jd_keywords": total_jd_keywords,
        "matched_count": len(matched),
        "readiness": readiness,
        "badge_class": badge_class,
        "advice": advice,
        "recommendations": recommendations
    }

def generate_student_resume_text(student_id):
    """
    Constructs an ATS-formatted resume summary string for a registered student
    incorporating their department, CGPA, verified skills, and academic profile.
    """
    student = get_student_by_id(student_id)
    if not student:
        return ""

    skills_names = [s["skill_name"] for s in student.get("skills", [])]
    cgpa_str = f"{float(student['cgpa']):.2f}" if student.get("cgpa") else "7.80"

    resume_text = f"""
Candidate Name: {student['student_name']}
Roll Number: {student['roll_no']}
Education: Bachelor of Technology (B.Tech) in {student['department']}
Graduation Batch: Class of {student['graduation_year']}
Academic Standing: Cumulative GPA {cgpa_str} / 10.0
Placement Status: {'Eligible for Campus Recruitment Drives' if student.get('eligible_for_placement') else 'Ineligible'}

TECHNICAL COMPETENCIES & SKILLS:
{', '.join(skills_names) if skills_names else 'Data Structures & Algorithms, Python, SQL, Problem Solving'}

ACADEMIC & CAPSTONE PROJECTS:
- Placement Analytics System: Developed a full-stack data analytics and machine learning platform using Python, Flask, MySQL, and Scikit-Learn.
- Engineered predictive classification algorithms to evaluate student placement readiness and salary package forecasting.
- Designed relational database schemas in MySQL with index optimization and parameterized queries.
- Built interactive web interfaces with HTML, CSS, JavaScript, and Bootstrap 5.

EXPERIENCE & CERTIFICATIONS:
- Active participant in technical coding challenges (LeetCode, HackerRank) focusing on Data Structures and Algorithms.
- Proficient with Git version control, GitHub workflows, REST APIs, and Linux fundamentals.
- Strong team communication, problem solving, and analytical thinking abilities.
"""
    return resume_text.strip()
