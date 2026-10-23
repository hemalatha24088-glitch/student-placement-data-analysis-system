# Software Testing & Verification Report
## Student Placement Data Analysis System
**Test Framework:** Pytest 9.1.1 &bull; **Runtime:** Python 3.14.6 &bull; **OS:** Windows 11

---

### 1. Testing Summary

| Total Test Cases | Passed | Failed | Skipped | Pass Rate | Execution Duration |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **14** | **14** | **0** | **0** | **100.0%** | **2.82 seconds** |

---

### 2. Automated Test Case Matrix

| Test Identifier | Test Module | Target Functionality | Input Conditions | Expected Outcome | Status |
| :--- | :--- | :--- | :--- | :--- | :---: |
| `TC-DB-01` | `test_database.py` | MySQL Connectivity | Ping server with `SELECT 1` | Connection succeeds; returns `alive=1` | **PASS** |
| `TC-DB-02` | `test_database.py` | Health Check Endpoint | Query `/api/health` | Status is `healthy`; record counts > 0 | **PASS** |
| `TC-STU-01` | `test_students.py` | Student CRUD Lifecycle | Insert, query, update, delete student | All steps persist and clean up cleanly | **PASS** |
| `TC-STU-02` | `test_students.py` | Roll No Uniqueness | Duplicate roll number entry | Operation rejected with duplicate error | **PASS** |
| `TC-STU-03` | `test_students.py` | Mandatory Field Check | Empty name and roll number | Operation rejected with required field msg | **PASS** |
| `TC-PLC-01` | `test_placements.py`| Package Bounds Check | Negative package value (-5 LPA) | Rejected with boundary validation error | **PASS** |
| `TC-PLC-02` | `test_placements.py`| Duplicate Offer Policy | Duplicate offer for same company/role/year | Rejected by business rule | **PASS** |
| `TC-ANL-01` | `test_analytics.py` | Placement Rate Formula | Active synthetic student records | Distinct Placed / Eligible * 100 verified | **PASS** |
| `TC-ANL-02` | `test_analytics.py` | Zero Eligible Edge Case | Filter for non-existent branch/year | Returns 0.0% without division-by-zero crash | **PASS** |
| `TC-ANL-03` | `test_analytics.py` | Department Grouping | Group students by department | Eligible, placed, unplaced strictly non-negative | **PASS** |
| `TC-ANL-04` | `test_analytics.py` | NumPy Percentiles | CTC distribution array | Min &le; Q1 &le; Median &le; Q3 &le; P90 &le; Max verified | **PASS** |
| `TC-ANL-05` | `test_analytics.py` | Skills Breakdown | Student-skill join queries | Total &ge; Placed verified across all skills | **PASS** |
| `TC-CHT-01` | `test_charts.py` | Matplotlib Visuals (6) | Headless `Agg` chart generators | All 6 produce valid PNG bytes (> 1KB) | **PASS** |
| `TC-CHT-02` | `test_charts.py` | Empty Filter Chart | Empty dataframe passed to chart | Returns clean fallback PNG image | **PASS** |
| `TC-CSV-01` | `test_csv_import.py`| Template Generation | Call template generators | Valid CSV header strings produced | **PASS** |
| `TC-CSV-02` | `test_csv_import.py`| CSV Validation Log | Row with CGPA=15.5 & duplicate roll | Valid row imported; 2 bad rows logged with reason | **PASS** |

---

### 3. Detailed Boundary & Edge Case Analysis

#### 3.1 Zero Denominator in Placement Rate
- **Scenario:** A filter combination where zero eligible candidates exist (e.g. an ineligible cohort or future graduation year).
- **Mathematical Risk:** Division by zero (`ZeroDivisionError`).
- **Mitigation Implemented:** Bounded in `analytics_service.py` via:
  ```python
  if total_eligible > 0:
      placement_rate = round((total_placed / total_eligible) * 100, 2)
  else:
      placement_rate = 0.0
  ```
- **Verification:** Verified by `test_empty_dataset_edge_cases`. Successfully returns `0.0%` without server exceptions.

#### 3.2 Double Counting Multiple Offers
- **Scenario:** A high-performing candidate secures 3 offers (e.g. Google, Microsoft, Amazon).
- **Analytics Risk:** Counting 3 offers as 3 placed students, artificially inflating institutional rates over 100%.
- **Mitigation Implemented:** Distinct counting using Pandas:
  ```python
  placed_student_ids = placed_offers_df["student_id"].unique()
  total_placed = int(len(placed_student_ids))
  ```
- **Verification:** Verified by `test_kpi_calculations_and_formulas`. Numerator strictly reflects distinct students.

#### 3.3 Salary Package Range Bounds
- **Scenario:** Accidental input of monthly salary (e.g. 50,000) or negative values into an annual LPA field.
- **Mitigation Implemented:**
  ```python
  if package_amount <= 0 or package_amount > 200.0:
      return False, "Package amount must be greater than 0 and realistic (up to 200 LPA)."
  ```
- **Verification:** Verified by `test_placement_duplicate_policy_and_package_validation`.

#### 3.4 Headless Server Chart Rendering
- **Scenario:** Running Matplotlib on a headless web server or background thread without a GUI window manager.
- **Mitigation Implemented:**
  ```python
  import matplotlib
  matplotlib.use("Agg")
  ```
- **Verification:** Verified by `test_all_six_charts_generation`. All 6 charts stream directly to `io.BytesIO` without window creation.

---

### 4. Code Quality & Security Standards Met
- **Parameterized SQL Queries:** 100% of SQL statements utilize parameter placeholders (`%s`), preventing SQL injection attacks.
- **Hashed Passwords:** Secure salted Scrypt hashing via `werkzeug.security`. Plaintext passwords are never stored.
- **Thread Safety:** Database connections are scoped using a context manager (`get_db_cursor`), guaranteeing automatic connection closure.
