# Verification, Testing & Coverage Report

**Date of Verification:** October 2026  
**Test Suite Status:** 104 / 104 Passed (100% Pass Rate)  
**Overall Code Coverage:** 85%  
**Framework:** Pytest 9.1.1, pytest-cov 7.1.0  
**Linter & Formatter:** Ruff 0.17.2, Black 26.10.1 (0 errors)

---

## 1. Test Suite Summary Table

| Test Suite Module | File Path | Tests | Status | Description |
| :--- | :--- | :---: | :---: | :--- |
| **RBAC Security** | `tests/test_rbac.py` | 5 | PASSED | Validates least-privilege matrix across Anonymous, Student, Officer, and Admin. |
| **CSRF Protection** | `tests/test_csrf.py` | 4 | PASSED | Enforces CSRF token requirement on POST operations; verifies 400 rejection. |
| **CSV Security** | `tests/test_csv_security.py` | 4 | PASSED | Formula injection sanitization (`=`, `+`, `-`, `@`) and row count cap (1,000 max). |
| **Auth & Rate Limiting** | `tests/test_auth.py` | 17 | PASSED | Login, student-only register, 5 req/min rate limit (429), password policy, OAuth hiding. |
| **Admin Management** | `tests/test_admin_management.py` | 3 | PASSED | Role promotion, admin password resets, self-demotion & self-deletion blocks. |
| **OpenAPI & Swagger** | `tests/test_api_docs.py` | 3 | PASSED | Tests OpenAPI 3.0.3 YAML spec, Swagger UI HTML bundle, and Chart.js JSON dataset API. |
| **Model Info & Metrics** | `tests/test_model_info.py` | 6 | PASSED | `/model-info`, Joblib persistence, zero data leakage, and 5-fold CV consistency. |
| **Main Routes & Health** | `tests/test_main_routes.py` | 6 | PASSED | Landing redirect, overview showcase, HTML/JSON health check (`/api/health`). |
| **Placement Predictor** | `tests/test_ml_predictor.py` | 5 | PASSED | Random Forest inference, probability gauge, risk classification, and retraining. |
| **Salary Regressor** | `tests/test_salary_predictor.py` | 7 | PASSED | CTC Package regressor, confidence bands, salary tier, and retraining. |
| **Skills & Recommender** | `tests/test_skill_recommender.py` | 7 | PASSED | Gap analysis, roadmap generation, skill directory CRUD, and JSON API reactivity. |
| **NLP ATS Matcher** | `tests/test_nlp_ats.py` | 6 | PASSED | Text cleaning, TF-IDF cosine similarity, keyword extraction, and match scores. |
| **Import & Uploads** | `tests/test_import_routes.py` | 6 | PASSED | CSV file upload validation, extension checking, and CSV template generation. |
| **CSV Import Services** | `tests/test_csv_import.py` | 2 | PASSED | Stream parser and validation logic for student and placement spreadsheets. |
| **Analytics & KPIs** | `tests/test_analytics.py` | 5 | PASSED | Placement rates, median/mean packages, percentile calculations with NumPy. |
| **Analytics & Reports** | `tests/test_analytics_and_reports.py` | 4 | PASSED | Sub-views, chart data JSON API (`/api/chart-data`), and 6 CSV report exports. |
| **Chart Generators** | `tests/test_charts.py` | 2 | PASSED | Matplotlib PNG buffer generation and graceful empty dataset handling. |
| **Companies CRUD** | `tests/test_companies.py` | 2 | PASSED | Complete CRUD lifecycle for recruiting companies. |
| **Placements Management** | `tests/test_placements.py` | 3 | PASSED | Duplicate offer policy and parameter filtering. |
| **Placements CRUD** | `tests/test_placements_crud.py` | 2 | PASSED | End-to-end HTTP lifecycle for placement offers. |
| **Students CRUD** | `tests/test_students.py` | 3 | PASSED | Student creation, GPA validation, resume view, and deletion. |
| **Database Connection** | `tests/test_database.py` | 2 | PASSED | DictCursor contexts, SSL configuration, and ping health diagnostics. |
| **TOTAL** | **22 Modules** | **104** | **100%** | **All 104 tests pass without regression.** |

---

## 2. Code Coverage Breakdown by Module

```text
Name                                        Stmts   Miss  Cover
---------------------------------------------------------------
app\limiter.py                                  3      0   100%
app\routes\main.py                             50      0   100%
app\routes\analytics.py                        40      0   100%
app\routes\reports.py                         103      1    99%
app\services\large_seed_service.py            104      2    98%
app\routes\api.py                              56      2    96%
app\services\chart_service.py                 170      7    96%
app\services\ml_service.py                    352     28    92%
app\routes\admin.py                            64      6    91%
app\services\placement_service.py             121     12    90%
app\services\nlp_service.py                    73      7    90%
app\services\analytics_service.py             146     14    90%
app\services\skill_service.py                  45      6    87%
app\routes\ats.py                              44      6    86%
app\routes\students.py                         99     15    85%
app\services\student_service.py               122     19    84%
app\services\company_service.py                61     10    84%
app\routes\placements.py                       61     10    84%
app\routes\companies.py                        57     10    82%
app\routes\predictor.py                       144     29    80%
app\routes\skills.py                          102     22    78%
app\services\import_service.py                154     36    77%
app\__init__.py                               104     28    73%
app\routes\import_export.py                    75     20    73%
app\database\connection.py                     47     13    72%
app\routes\auth.py                            208     75    64%
app\services\skill_recommender_service.py      73     26    64%
app\utils\auth.py                              59     21    64%
---------------------------------------------------------------
TOTAL                                        2737    410    85%
```

---

## 3. How to Run Verification

### Run Pytest with Terminal Coverage Report
```bash
pytest tests/ --cov=app --cov-report=term-missing
```

### Run Ruff Code Quality Linter
```bash
ruff check app tests
```

### Run Black Code Style Formatter
```bash
black --check app tests
```
