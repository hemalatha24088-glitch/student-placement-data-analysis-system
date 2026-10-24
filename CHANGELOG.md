# Changelog

All notable changes to the **Student Placement Data Analysis System** project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.0] - 2026-10-24

### Major Production & Security Overhaul (10/10 Engineering Standard)

This landmark release transforms the Student Placement Data Analysis System into an enterprise-ready, accessible, fully tested, and secure analytical platform.

### Added
- **Security Hardening (Phase 1):**
  - Fail-fast environment variable validation in `config.py` raising clear `RuntimeError` if `SECRET_KEY` or `DB_PASSWORD` are absent. Defaulted `DEBUG` to `False`.
  - Comprehensive Role-Based Access Control (RBAC) with `@login_required`, `@role_required`, and `@student_self_or_staff_required` decorators across all routes.
  - Public registration restricted strictly to the `Student` role; administrative promotion portal at `/admin/users`.
  - CSRF protection across all forms and API endpoints using Flask-WTF. All deletion endpoints converted to POST with CSRF verification.
  - Secure session cookie configuration (`SESSION_COOKIE_HTTPONLY=True`, `SESSION_COOKIE_SAMESITE="Lax"`, `SESSION_COOKIE_SECURE=True`).
  - IP-based rate limiting via Flask-Limiter (5 requests/min on `/login` and `/register`) with generic credential error messages.
  - Production security headers enforced via Flask-Talisman (CSP, X-Content-Type-Options, X-Frame-Options, Referrer-Policy).
  - Explicit `DEMO_MODE=true` environment flag; demo login buttons and credentials are now completely suppressed in production by default.
  - CSV injection defense: sanitized cells starting with `=`, `+`, `-`, `@`, `\t`, `\r` with prepended `'`; capped batch CSV imports at 1,000 rows with secure filename sanitization.
  - Custom error handling templates for HTTP 403, 404, and 500 without stack trace leaks.
- **Honest Authentication & Lifecycle (Phase 2):**
  - Genuine Google OAuth 2.0 integration via `Authlib` (`/auth/login/google`, `/auth/callback/google`). If client credentials are unset, the Google button is completely hidden.
  - User password change self-service portal (`/auth/change-password`) and admin-initiated password resets (`/admin/users/<id>/reset-password`).
  - Password complexity validator enforcing minimum 8 characters, mixed-case letters, digits, and special characters.
- **Machine Learning & Data Integrity (Phase 3):**
  - Empirical Model Performance Hub at `/model-info` presenting real computed statistics: Random Forest Placement Classifier (Accuracy: 79.55%, Precision: 0.81, Recall: 0.72, F1: 0.76, ROC-AUC: 0.85, 5-Fold CV Mean: 80.39%) and Salary Package Regressor (MAE: 2.83 LPA, RMSE: 3.51 LPA, $R^2$: 0.44, 5-Fold CV MAE: 3.01 LPA).
  - `joblib` model serialization avoiding retraining on each web request, with on-demand `/predictor/retrain` endpoint.
  - Zero data leakage audit: verified and enforced that post-hire attributes (e.g., placement status, package) are never present in feature training matrices.
  - Low-data-volume (< 200 students) amber warning banners and clear statistical disclaimers on all prediction pages.
  - Synthetic dataset generator (`python init_db.py --large-seed`) generating 639 students, 382 placements, and 3,000+ skill tags.
  - Interactive feature importance visualization on the placement predictor interface.
- **Testing & Code Quality (Phase 4):**
  - Pytest test suite expanded to **101 comprehensive unit and integration tests** across 21 test suites.
  - Verified **85% code coverage** across the application core (`pytest --cov=app`).
  - PEP-484 type annotations and Google-style docstrings across all service layers.
  - Structured rotating file logging (`logs/app.log`, 10MB per file, 5 backup rotations); eliminated stray `print()` calls.
  - Code formatting with `black` (120 line length) and linting with `ruff` (`pyproject.toml`).
  - GitHub Actions CI/CD pipeline (`.github/workflows/ci.yml`) spinning up MySQL 8.0, running Ruff, Black, database migrations, and Pytest coverage checks.
  - Strictly pinned production dependencies in `requirements.txt` and tooling in `requirements-dev.txt`.
- **UI/UX Design & Interactivity (Phase 5):**
  - Refined Navy & Indigo modern design system using Inter font family and CSS custom variables.
  - Dark / Light mode toggle persisting user preference in `localStorage` with OS `prefers-color-scheme` support.
  - Fully responsive mobile drawer navigation with hamburger toggle and overlay backdrop.
  - Modern Chart.js 4.4.1 interactive visualizations replacing static Matplotlib PNGs on the dashboard (tooltips, legend toggling, and client-side PNG export). Matplotlib rendering preserved for printable PDF/paper reports.
  - Client-side table search, column sorting, and pagination for students, companies, and placement tables.
  - Interactive "What-If" prediction simulator with live CGPA sliders, skill toggles, and animated SVG probability gauge.
  - Accessible forms with loading indicators, button debounce protection, and modal confirmations for destructive actions.
  - Dedicated `app/static/css/print.css` stylesheet for executive reports and student biodata printing.
- **Production Deployment & Migrations (Phase 6):**
  - Production `Procfile` configured for Gunicorn with dynamic `$PORT` binding.
  - Containerized deployment ready via multi-stage `Dockerfile` and `docker-compose.yml`.
  - JSON health monitor endpoint at `/api/health` providing database ping and latency metrics.
  - Database migration runner (`migrations/migrate.py`) with idempotent SQL versions (`001_initial_schema.sql`, `002_add_indexes_and_constraints.sql`) and `schema_migrations` tracking.
  - Automated database backup utility (`scripts/backup_db.py`) supporting `mysqldump` with automatic pure-Python fallback.
  - Comprehensive `render.yaml` configuration for zero-downtime PaaS deployment.
- **Documentation & OpenAPI (Phase 7):**
  - OpenAPI 3.0.3 specification (`docs/openapi.yaml`) with embedded Swagger UI at `/api/docs`.
  - Defense-in-depth architecture document (`docs/security.md`).
  - Verified testing report (`docs/testing_report.md`) detailing all 101 tests and coverage matrix.
  - Step-by-step deployment guide for Render, Aiven, Railway, and Docker (`docs/deployment_guide.md`).
  - Open-source assets: `LICENSE` (MIT), `CONTRIBUTING.md`, `CHANGELOG.md`, and GitHub issue templates.

### Changed
- Parameterized all dynamic SQL queries across student, analytics, placement, and skill services.
- Replaced hardcoded credential fallbacks with strict environment configuration.
- Replaced static PNG charts on dashboard with dynamic Chart.js canvas renderings.

### Removed
- Removed hardcoded credentials, default fallback passwords, and weak default secret keys across all files.
- Removed cloudflare tunnel binaries and all tunnel provider references.
- Removed simulated Google OAuth fallback; unconfigured OAuth buttons are now hidden completely.

---

## [1.0.0] - 2026-10-23
- Initial MVP release of Flask + MySQL Student Placement Data Analysis System.
- Basic CRUD operations for students, companies, and placements.
- Machine learning placement probability prediction and salary estimation.
- Static Matplotlib visualization generation.
