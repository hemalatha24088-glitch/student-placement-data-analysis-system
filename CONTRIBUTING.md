# Contributing to Student Placement Data Analysis System

Thank you for your interest in contributing to the **Student Placement Data Analysis System**! We welcome contributions, bug reports, and enhancements from developers, data scientists, and educators.

Please take a moment to review this document before submitting issues or pull requests.

---

## Code of Conduct

We are committed to providing a welcoming, inclusive, and harassment-free environment for everyone. Please be respectful and constructive in all discussions, issues, and pull requests.

---

## Development Setup

### 1. Prerequisites
- **Python 3.10+** (Python 3.11 recommended)
- **MySQL 8.0+** (Local service, Docker, or hosted instance such as Aiven/Railway)
- **Git**

### 2. Clone the Repository
```bash
git clone https://github.com/hemalatha24088-glitch/student-placement-data-analysis-system.git
cd student-placement-data-analysis-system
```

### 3. Create and Activate a Virtual Environment
- **Windows (PowerShell):**
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  ```
- **macOS / Linux (Bash):**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

### 4. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 5. Configure Environment Variables
Copy `.env.example` to `.env` and fill in your local MySQL credentials:
```bash
cp .env.example .env
```
Ensure you provide strong development secrets (never commit your `.env` file!):
```env
SECRET_KEY=your_secure_development_secret_key_minimum_32_characters
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=placement_db
DB_USER=root
DB_PASSWORD=your_local_mysql_password
DEMO_MODE=true
```

### 6. Initialize Database and Migrations
Run the database migrations and seed script:
```bash
python migrations/migrate.py
python init_db.py --create-admin
```
Optionally generate the large synthetic dataset (639 students, 382 placements):
```bash
python init_db.py --large-seed
```

### 7. Run the Local Development Server
```bash
python run.py
```
Visit `http://127.0.0.1:5000` in your browser.

---

## Branching & Workflow

1. Fork the repository and create your feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bugfix-name
   ```
2. Make modular, well-tested commits with descriptive messages following Conventional Commits:
   - `feat: add PDF resume extraction for ATS matching`
   - `fix: resolve division by zero in zero-placement departments`
   - `docs: update deployment instructions for AWS ECS`
   - `test: add edge cases for role-based access control`
3. Push your branch to GitHub and open a Pull Request targeting `main`.

---

## Code Quality Standards

Before submitting a Pull Request, ensure your code satisfies our linting and formatting standards:

### 1. Code Formatting (Black)
We use `black` with a line length of 120 characters:
```bash
black --check app tests migrations scripts
# To auto-format:
black app tests migrations scripts
```

### 2. Linting (Ruff)
We use `ruff` for fast Python linting:
```bash
ruff check app tests migrations scripts
# To auto-fix safe rules:
ruff check --fix app tests migrations scripts
```

### 3. Type Annotations & Docstrings
- All new service functions must include PEP-484 type annotations and descriptive docstrings explaining parameters, return types, and exceptions raised.
- Avoid raw `print()` statements in application code; use the structured logger:
  ```python
  import logging

  logger = logging.getLogger(__name__)
  logger.info("Retraining completed successfully.")
  ```

---

## Testing Guidelines

We enforce a strict **minimum 85% code coverage** standard across the application layer.

### Running Pytest
```bash
pytest
```

### Running with Code Coverage
```bash
pytest tests/ --cov=app --cov-report=term-missing --cov-fail-under=85
```

All 101+ tests must pass before any Pull Request is merged. When adding a new feature or fixing a bug, write matching unit and integration tests under `tests/`.

---

## Security Guidelines

- **Never hardcode secrets** or credentials in any file. Use `os.environ` exclusively.
- All SQL queries must be parameterized (`cursor.execute(sql, (param1, param2))`). String interpolation in SQL is strictly prohibited.
- All mutating endpoints (`POST`, `PUT`, `DELETE`) must enforce CSRF protection via Flask-WTF.
- If you discover a security vulnerability, please do NOT file a public issue. See [`docs/security.md`](docs/security.md) for responsible disclosure instructions.

---

## Pull Request Checklist

Before submitting:
- [ ] Code adheres to Black (120 chars) and Ruff rules.
- [ ] Type annotations and docstrings are provided on new services.
- [ ] All 101+ tests pass with `pytest`.
- [ ] Overall test coverage remains $\ge 85\%$.
- [ ] No secrets or personal environment values are committed.
- [ ] Relevant documentation under `docs/` is updated.
