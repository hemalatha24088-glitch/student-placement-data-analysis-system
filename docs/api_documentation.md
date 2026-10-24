# REST API & OpenAPI Documentation
## Student Placement Data Analysis System

The application exposes structured REST, JSON analytics, and data streaming endpoints to support real-time frontend reactivity, interactive Chart.js visualizations, live what-if ML predictions, and data export.

Interactive OpenAPI/Swagger documentation is available directly in the browser at:
- **Swagger UI:** `http://127.0.0.1:5000/api/docs`
- **Raw OpenAPI 3.0.3 YAML:** `http://127.0.0.1:5000/api/openapi.yaml` (also located at [`docs/openapi.yaml`](openapi.yaml))

---

### 1. Base URL
```text
http://127.0.0.1:5000/
```

---

### 2. Authentication & Authorization

All endpoints modifying state or accessing protected records require active session cookies authenticated via `/login` or Google OAuth.
- **CSRF Protection:** All state-modifying requests (`POST`, `PUT`, `DELETE`) require a valid `X-CSRFToken` header or `csrf_token` form field.
- **Rate Limiting:** Public authentication endpoints (`/login`, `/register`) are rate-limited to 5 requests per minute per IP address.
- **HTTP Status Codes:**
  - `200 OK`: Request succeeded.
  - `400 Bad Request`: Validation failure or malformed payload.
  - `401 Unauthorized`: Authentication required.
  - `403 Forbidden`: Authenticated user lacks required role permissions.
  - `404 Not Found`: Resource does not exist.
  - `429 Too Many Requests`: Rate limit exceeded.
  - `500 Internal Server Error`: Server error (logged without exposing stack traces).

---

### 3. API Endpoints Reference

#### 3.1 System Health Diagnostic
Verifies relational database connectivity, MySQL server version, and table record counts. Used by container health checks and cloud orchestrators.

- **URL:** `/api/health`
- **Method:** `GET`
- **Authentication:** Public
- **Response Format:** `application/json`

**Example Response:**
```json
{
  "connected": true,
  "database_name": "placement_db",
  "server_version": "8.0.46",
  "status": "healthy",
  "tables": {
    "companies": 28,
    "placements": 382,
    "skills": 42,
    "students": 639
  }
}
```

---

#### 3.2 Dynamic Chart.js Analytics Data
Returns structured JSON data formatted for Chart.js 4.4.1 components on the analytics dashboard.

- **URL:** `/api/chart-data`
- **Method:** `GET`
- **Authentication:** Required (`student`, `placement_officer`, `admin`)
- **Query Parameters:**
  - `department` (optional, string): Filter by department or `All`
  - `graduation_year` (optional, int): Filter by graduation year or `All`
- **Response Format:** `application/json`

**Example Response:**
```json
{
  "department_rates": [
    {"department": "Computer Science and Engineering", "placement_rate": 86.4, "total_students": 140, "placed_students": 121},
    {"department": "Information Technology", "placement_rate": 81.2, "total_students": 112, "placed_students": 91}
  ],
  "placed_vs_eligible": {
    "departments": ["CSE", "IT", "ECE", "EEE", "Mech"],
    "eligible": [135, 108, 95, 78, 62],
    "placed": [121, 91, 74, 52, 38]
  },
  "package_distribution": {
    "bins": ["0-4 LPA", "4-8 LPA", "8-12 LPA", "12-16 LPA", "16-20 LPA", "20+ LPA"],
    "counts": [45, 120, 110, 62, 30, 15]
  },
  "top_skills": [
    {"skill_name": "Python", "placed_count": 182},
    {"skill_name": "SQL", "placed_count": 164},
    {"skill_name": "Java", "placed_count": 145}
  ],
  "company_hires": [
    {"company_name": "Google", "hires": 14, "avg_package": 28.5},
    {"company_name": "Microsoft", "hires": 18, "avg_package": 26.2}
  ],
  "yearly_trends": [
    {"graduation_year": 2024, "avg_package_lpa": 8.4, "placement_rate": 78.2},
    {"graduation_year": 2025, "avg_package_lpa": 9.2, "placement_rate": 82.5},
    {"graduation_year": 2026, "avg_package_lpa": 10.1, "placement_rate": 85.0}
  ]
}
```

---

#### 3.3 Live KPI Statistics
Returns calculated headline KPIs and counts matching selected filter criteria.

- **URL:** `/api/stats`
- **Method:** `GET`
- **Authentication:** Required (`student`, `placement_officer`, `admin`)
- **Query Parameters:**
  - `department` (optional, string)
  - `graduation_year` (optional, int)
  - `status` (optional, string)
  - `company_id` (optional, int)
- **Response Format:** `application/json`

**Example Response:**
```json
{
  "filters": {
    "company_id": "All",
    "department": "Computer Science and Engineering",
    "graduation_year": "2026",
    "status": "All"
  },
  "kpis": {
    "avg_package": 12.8,
    "highest_package": 36.0,
    "lowest_package": 4.5,
    "median_package": 11.5,
    "placement_rate": 86.4,
    "sample_label": "Synthetic Academic Data",
    "total_companies": 28,
    "total_eligible": 135,
    "total_placed": 121,
    "total_students": 140,
    "unplaced_students": 19
  },
  "success": true
}
```

---

#### 3.4 Interactive What-If Placement Predictor
Computes real-time placement probability and risk tier from student profile attributes and active skill selections without persisting records.

- **URL:** `/predictor/api/predict`
- **Method:** `POST`
- **Authentication:** Required (`student`, `placement_officer`, `admin`)
- **Headers:** `Content-Type: application/json`, `X-CSRFToken: <token>`
- **Request Body:**
```json
{
  "cgpa": 8.75,
  "department": "Computer Science and Engineering",
  "internships": 2,
  "projects": 3,
  "certifications": 2,
  "backlogs": 0,
  "skills": ["Python", "SQL", "Machine Learning", "Docker"]
}
```
- **Response Format:** `application/json`

**Example Response:**
```json
{
  "probability": 87.5,
  "risk_tier": "Low Risk",
  "risk_color": "#10b981",
  "key_factors": [
    {"feature": "CGPA", "contribution": "High Positive"},
    {"feature": "Internships", "contribution": "Positive"},
    {"feature": "Backlogs", "contribution": "Neutral"}
  ],
  "disclaimer": "Predictions are statistical estimates based on current training data and do not guarantee recruitment outcomes."
}
```

---

#### 3.5 Fallback Matplotlib Chart Streaming
Generates and streams server-rendered static Matplotlib binary PNGs (used for PDF generation and printable reports).

- **URL:** `/api/charts/<chart_name>`
- **Method:** `GET`
- **Authentication:** Required
- **Supported `chart_name` values:**
  - `dept-rate`: Department-Wise Placement Rate
  - `placed-vs-eligible`: Placed vs Eligible Student Volumes
  - `package-distribution`: CTC Distribution Histogram
  - `top-skills`: Top In-Demand Skills
  - `company-hires` (or `company-recruitment`): Company Hires & CTC
  - `yearly-trends`: Longitudinal Placement Trends
- **Response Format:** `image/png`

---

#### 3.6 Data Export & Templates
- **CSV Data Export:** `/reports/export-csv?type=<summary|department|students|companies|packages|skills>` (Role: `placement_officer`, `admin`)
  - Sanitized against CSV formula injection (`=`, `+`, `-`, `@` escaped).
- **CSV Import Templates:** `/import/template/<students|placements>` (Role: `placement_officer`, `admin`)
