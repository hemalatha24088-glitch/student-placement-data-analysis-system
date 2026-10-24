# Student Placement Data Analysis System
### A Full-Stack Analytics & AI/ML Platform for College Placement Management
**Academic Capstone Project &bull; B.Tech Computer Science & Engineering (AI/ML)**

[![GitHub Repo](https://img.shields.io/badge/GitHub-Public%20Repository-blue?logo=github)](https://github.com/hemalatha24088-glitch/student-placement-data-analysis-system)
[![Python](https://img.shields.io/badge/Python-3.14-blue?logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1-black?logo=flask)](https://flask.palletsprojects.com)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-orange?logo=mysql)](https://mysql.com)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.9-orange?logo=scikit-learn)](https://scikit-learn.org)
[![Tests](https://img.shields.io/badge/Pytest-48%20Passed-brightgreen)](https://pytest.org)

---

## 🌐 Public Live Access & Quick Demo

Anyone on the internet can test and interact with the live running application:

- **Live Public URL:** [https://educational-tony-sunglasses-punch.trycloudflare.com](https://educational-tony-sunglasses-punch.trycloudflare.com)
- **Direct Sign-In Portal:** [https://educational-tony-sunglasses-punch.trycloudflare.com/login](https://educational-tony-sunglasses-punch.trycloudflare.com/login)
- **Direct New User Registration:** [https://educational-tony-sunglasses-punch.trycloudflare.com/register](https://educational-tony-sunglasses-punch.trycloudflare.com/register)

### 🔐 How Anyone Can Log In:
1. **Create Your Own Account (Sign Up):** 
   - Click **[Sign Up](https://educational-tony-sunglasses-punch.trycloudflare.com/register)** on the login screen.
   - Enter your **Full Name**, choose your own **Username** &amp; **Password**, select your **Role** (Placement Officer, Administrator, or Student), and optionally add your email.
   - Your account is immediately saved in the MySQL database and you are logged into the dashboard!
   - Next time you return, simply type your username (or email) and password on `/login`.
2. **Login with Google Account:** 
   - Click **"Login with Google Account"** on `/login` or `/register`.
   - Enter your personal or institutional Google email (or click the quick demo option) to sign in with an official Google badge.
3. **One-Click Faculty / Admin Evaluator Demo:** 
   - Click **"Faculty Officer"** or **"Administrator"** on the login screen for instant, one-click viva evaluation access.
4. **Pre-configured Accounts:**
   - **Faculty / Placement Officer:** `faculty` / `faculty123`
   - **System Administrator:** `admin` / `admin123`

---

## 1. Project Overview

The **Student Placement Data Analysis System** is a professional, full-stack web application designed to track, analyze, predict, and visualize student recruitment performance across academic departments, salary tiers, hiring companies, and verified technical skills.

Built using **Python 3**, **Flask**, **MySQL 8.0**, **Scikit-Learn**, **Pandas**, **NumPy**, and **Matplotlib**, this system moves college placement operations away from fragmented manual spreadsheets into an automated, relational, and auditable analytical platform.

> **Demonstration Notice:** The dataset pre-loaded into the database contains **synthetic sample data** structured specifically for college project reviews, algorithm verification, and faculty viva examination.

---

## 2. Technology Stack

- **Backend:** Python 3.14+, Flask 3.1
- **Database:** MySQL Server 8.0 (Relational schema with InnoDB, Foreign Keys, Indexes)
- **Database Driver:** PyMySQL 1.2 & MySQL Connector Python
- **Machine Learning & NLP:** Scikit-Learn 1.9 (RandomForestClassifier, GradientBoostingClassifier, RandomForestRegressor, TF-IDF Vectorizer, Cosine Similarity)
- **Data Analytics:** Pandas 3.1 (aggregations, multi-table grouping, CSV processing)
- **Numerical Calculations:** NumPy 2.5 (mean, median, standard deviation, percentiles)
- **Data Visualizations:** Matplotlib 3.11 (headless `Agg` engine generating responsive PNG charts)
- **Frontend UI/UX:** HTML5, CSS3 (Modern Navy/Indigo SaaS Design System), Vanilla JavaScript
- **Testing:** Pytest 9.1 (48 automated unit & integration tests)

---

## 3. Key Features

1. **Mandatory Sign-In First Portal (`/login` & `/register`):**
   - Unauthenticated visitors are automatically directed to the secure sign-in portal.
   - Self-registration with encrypted password hashing (`werkzeug.security`).
   - Dual-mode credential authentication (sign in with Username OR registered Email).
   - Google Account SSO integration.
   - One-click Faculty and Administrator demonstration access.
2. **Interactive Analytics Dashboard (`/dashboard`):**
   - 8 live KPI metric cards (Registered, Eligible, Placed, Unplaced, Placement Rate %, Average CTC, Median CTC, Active Recruiters).
   - Global dynamic filter bar (Graduation Year, Department, Offer Status, Company).
   - 6 dynamic Matplotlib visualizations with instant image refresh and download capability.
   - Data-driven placement observations automatically generated from filtered records.
3. **Machine Learning Placement Probability Predictor (`/predictor`):**
   - Dual-model ML architecture (`RandomForestClassifier` & `GradientBoostingClassifier`).
   - Features: CGPA, Department, Skill Count, Graduation Year, Eligibility.
   - Interactive SVG Probability Gauge, confidence breakdown, top influential factors, and personalized recommendations.
   - Pre-computed candidate roster with high/medium/risk classification and cohort filtering.
4. **AI Skill Gap Analyzer & Learning Roadmap Recommender (`/recommender`):**
   - Curated hiring tier benchmarks (`Tier-1 Super Dream`, `Tier-2 Dream`, `Tier-3 Core Tech`, `Tier-4 IT Services`).
   - Match percentage scoring, verified student skills vs. missing high-yield skills.
   - Curated 4-week step-by-step learning roadmap with free learning resources.
5. **Machine Learning Salary Package (CTC) Regressor & Printable Bio-Data (`/salary-predictor`):**
   - `RandomForestRegressor` predicting estimated package in Lakhs Per Annum (LPA) (MAE $\pm$3.63 LPA).
   - What-if CGPA and technical skill scenario simulator.
   - Printable Candidate Resume / Placement Bio-Data generator (`/students/<id>/resume`).
6. **Natural Language Processing (NLP) ATS Resume & Job Description Matcher (`/ats`):**
   - TF-IDF Vectorizer and Cosine Similarity scoring.
   - Keyword frequency analysis and technical gap identification.
   - Live sample job descriptions (Google SDE-1, Microsoft Cloud Engineer, Data Analyst, TCS Digital).
7. **Student Management (`/students`):**
   - Complete CRUD (Create, Read, Update, Delete) with roll number uniqueness protection, CGPA tracking, placement eligibility controls, and skill associations.
8. **Company Management (`/companies`):**
   - Partner directory, hiring tiers (`Super Dream`, `Dream`, `Core Engineering`, `Mass / IT Services`), and average compensation tracking.
9. **Placement Records Registry (`/placements`):**
   - Job offer management in INR Lakhs Per Annum (LPA) CTC. Enforces business rule preventing duplicate active offers for the same student, company, and role in a given year.
10. **Deep Analytical Modules (`/analytics/`):**
    - Department-Wise Comparisons (`/analytics/departments`).
    - Salary Package Distributions, Percentiles & Tiers (`/analytics/packages`).
    - Historical Trends across Graduation Classes 2024–2026 (`/analytics/trends`).
11. **Reports & Dynamic CSV Export (`/reports`):**
    - Printable report sheets and one-click CSV export for summaries, department rolls, student rosters, and compensation brackets.
12. **Bulk CSV Data Import (`/import`):**
    - Upload spreadsheet callsets for students and placements with row-by-row error logging and sample CSV templates.

---

## 4. Windows Quickstart Guide (Step-by-Step)

### Prerequisites
- Windows 10 or 11
- Python 3.10+ installed
- MySQL Server 8.0 installed and running as a Windows service (`MySQL80`)

### Step 1: Open PowerShell in Project Folder
Navigate to the project root directory:
```powershell
cd "c:\Users\M Hemalatha\Desktop\spd"
```

### Step 2: Set Up Virtual Environment
Create and activate the Python virtual environment:
```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

### Step 3: Install Required Dependencies
Install the required packages using the virtual environment's pip:
```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Step 4: Configure Database Settings (`.env`)
The project reads credentials from `.env`. A default `.env` is already configured for local execution:
```ini
DB_HOST=localhost
DB_PORT=3307
DB_USER=root
DB_PASSWORD=aimlb4
DB_NAME=placement_db
SECRET_KEY=placement-data-analysis-secret-token-btech-aiml-2026
FLASK_ENV=development
FLASK_DEBUG=1
```
*(If your local MySQL runs on default port 3306 or has a different password, adjust `DB_PORT` and `DB_PASSWORD` accordingly).*

### Step 5: Initialize Schema & Seed Synthetic Data
Execute the automated database setup script:
```powershell
.\.venv\Scripts\python.exe init_db.py
```
*Output will confirm table creation and the insertion of initial synthetic sample records.*

### Step 6: Start the Web Application
Launch the Flask server:
```powershell
.\.venv\Scripts\python.exe run.py
```
You will see:
```text
=======================================================
 STUDENT PLACEMENT DATA ANALYSIS SYSTEM
 Local Web Server Running at: http://127.0.0.1:5000/
 Press CTRL+C to stop.
=======================================================
```

Open your browser and navigate to: **`http://127.0.0.1:5000/`**

---

## 5. Evaluation & Demo Login Credentials

For faculty evaluation, project viva review, and demonstration:
- **Sign Up / New User:** Click **[Sign Up](https://educational-tony-sunglasses-punch.trycloudflare.com/register)** to create any personal or institutional username & password.
- **Login with Google:** Click **"Login with Google Account"** on the login screen.
- **Faculty / Placement Officer:** Click **"Faculty Officer"** (or use username `faculty` / password `faculty123`).
- **System Administrator:** Click **"Administrator"** (or use username `admin` / password `admin123`).

---

## 6. Running Automated Tests

Run the full Pytest test suite:
```powershell
.\.venv\Scripts\python.exe -m pytest tests/ -v
```
All **48 unit & integration test suites** will execute across 11 test modules, covering:
- Mandatory Sign-In gateway and unauthenticated route blocking.
- User self-registration with duplicate username rejection and password confirmation validation.
- Dual-mode credential authentication (sign in with Username OR registered Email).
- Google Account SSO authentication and automatic profile provisioning.
- Machine Learning Placement Probability Predictor models (Random Forest & Gradient Boosting).
- Machine Learning Salary Package (CTC) Regressor (Random Forest Regressor, MAE validation).
- Natural Language Processing (NLP) ATS Resume & Job Description Matcher (TF-IDF & Cosine Similarity).
- AI Skill Gap Analyzer & Learning Roadmap generation.
- MySQL 8.0 connectivity and health verification.
- Student CRUD lifecycle and duplicate roll number rejection.
- Placement offer creation, duplicate offer prevention policy, and package boundary validation.
- Placement rate mathematical formulas (including division by zero prevention).
- Department aggregations and NumPy percentiles.
- Matplotlib headless chart generation (PNG magic bytes validation).
- CSV template generation and row-by-row error diagnostics.

---

## 7. Project Directory Structure

```text
spd/
├── app.py                      # Flask WSGI application entrypoint
├── run.py                      # Local development runner
├── config.py                   # Centralized configuration & environment loader
├── init_db.py                  # Database initialization & verification script
├── schema.sql                  # MySQL 8.0 DDL database schema
├── seed.sql                    # Synthetic sample dataset (57 students, 49 offers)
├── requirements.txt            # Python dependencies
├── .env                        # Local database credentials
├── .env.example                # Sample environment template
├── .gitignore                  # Git ignore rules
├── README.md                   # Complete documentation & Windows setup guide
├── app/
│   ├── __init__.py             # Application factory & Blueprint registration
│   ├── database/
│   │   └── connection.py       # Thread-safe PyMySQL DictCursor connection manager
│   ├── services/
│   │   ├── student_service.py   # Student CRUD & search filtering
│   │   ├── company_service.py   # Company directory & recruitment metrics
│   │   ├── skill_service.py     # Skills master & candidate associations
│   │   ├── placement_service.py # Placement offers & duplicate policy checks
│   │   ├── analytics_service.py # Pandas aggregations & NumPy calculations
│   │   ├── chart_service.py     # Headless Matplotlib visualization generator
│   │   └── import_service.py    # CSV validation & error diagnostics
│   ├── routes/
│   │   ├── main.py              # Landing page, Dashboard, Health check
│   │   ├── auth.py              # Authentication & one-click demo login
│   │   ├── students.py          # Student management routes
│   │   ├── companies.py         # Company management routes
│   │   ├── skills.py            # Skills directory routes
│   │   ├── placements.py        # Placement records routes
│   │   ├── analytics.py         # Department, Salary, Skill & Trend analytics
│   │   ├── reports.py           # Printable reports & CSV download routes
│   │   ├── import_export.py     # Bulk CSV upload routes
│   │   └── api.py               # REST API & dynamic chart streaming
│   ├── static/
│   │   ├── css/style.css        # Professional Navy/Indigo SaaS CSS system
│   │   └── js/
│   │       ├── main.js          # Alert auto-dismiss & confirmation modals
│   │       └── dashboard.js     # Dynamic chart reloading & image downloads
│   └── templates/
│       ├── base.html            # Sidebar + Topbar layout shell
│       ├── index.html           # Public SaaS Landing page
│       ├── dashboard.html       # Main Analytics Dashboard (8 KPIs, filters, charts)
│       ├── health.html          # Database health & diagnostics page
│       ├── auth/login.html      # Sign in page
│       ├── students/            # Student list, add/edit form, view profile
│       ├── companies/           # Company list, add/edit form, view hires
│       ├── skills/              # Skills directory
│       ├── placements/          # Placement offers list & form
│       ├── analytics/           # Dedicated analytical breakdown views
│       ├── reports/             # Multi-format report sheets
│       ├── import/              # CSV file upload & validation log
│       └── errors/              # Custom 404 & 500 error pages
├── tests/                       # Automated pytest test suites (14 tests)
├── sample_data/                 # Pre-generated sample CSV files
└── docs/                        # Formal academic project documentation
    ├── project_synopsis.md      # Full B.Tech project synopsis
    ├── database_design.md       # ER diagram & schema specifications
    ├── api_documentation.md     # REST API reference
    ├── testing_report.md        # Comprehensive test results report
    └── demo_script.md           # Presentation outline & Faculty viva Q&A
```

---

## 8. Placement Rate & Metric Formulas

### 1. Overall Placement Rate
$$\text{Placement Rate (\%)} = \left( \frac{\text{Distinct Eligible Students Counted as Placed}}{\text{Total Eligible Students}} \right) \times 100$$
- **Eligible Denominator:** Only students with `eligible_for_placement = 1` are included.
- **Distinct Placed Numerator:** Each eligible student with at least one confirmed offer (`Placed` or `Offer Accepted`) is counted exactly once, regardless of multiple offers.
- **Zero Denominator Guard:** If eligible students count is zero, the system returns `0.0%` (or `N/A`) preventing division-by-zero crashes.

### 2. Unplaced Eligible Candidates
$$\text{Unplaced Eligible} = \max(0, \text{Total Eligible Students} - \text{Distinct Placed Students})$$

### 3. Salary Package Statistics (LPA CTC)
- **Mean (Average):** $\mu = \frac{1}{N} \sum_{i=1}^{N} \text{Package}_i$
- **Median:** 50th percentile calculated using NumPy. Provides a robust measure of central tendency unaffected by super-dream outlier packages.
- **Percentiles:** 25th (Q1), 75th (Q3), and 90th percentiles calculated via `np.percentile`.

---

## 9. Troubleshooting & FAQ

- **Port Conflict (3306 vs 3307):** If your local MySQL Server runs on port 3306, update `DB_PORT=3306` in `.env`.
- **Access Denied Error:** Ensure `DB_PASSWORD` in `.env` matches your MySQL root password.
- **AppLocker / Script Policy on Windows:** If `pip.exe` is blocked, run pip as a Python module: `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`.
- **Chart Generation on Headless Machines:** Charts use `matplotlib.use('Agg')` which runs completely in-memory without requiring an X-server, display screen, or GUI window.
