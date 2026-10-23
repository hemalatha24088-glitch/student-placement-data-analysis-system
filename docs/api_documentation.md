# REST API Documentation
## Student Placement Data Analysis System

The application exposes structured REST and data streaming endpoints to support real-time frontend reactivity, dynamic chart generation, and data export.

---

### 1. Base URL
```text
http://127.0.0.1:5000/
```

---

### 2. Endpoints Reference

#### 2.1 System Health Diagnostic
Verifies relational database connectivity, MySQL server version, and table record counts.

- **URL:** `/api/health`
- **Method:** `GET`
- **Response Format:** `application/json`
- **Status Codes:**
  - `200 OK` (Database connected and functional)
  - `503 Service Unavailable` (Database unreachable)

**Example Response:**
```json
{
  "connected": true,
  "database_name": "placement_db",
  "server_version": "8.0.46",
  "status": "healthy",
  "tables": {
    "companies": 16,
    "placements": 49,
    "skills": 18,
    "students": 58
  }
}
```

---

#### 2.2 Live Analytics Statistics
Returns aggregated KPI counts and calculated metrics reflecting the provided query filters.

- **URL:** `/api/stats`
- **Method:** `GET`
- **Query Parameters:**
  - `department` (optional, string): Department name or `All`
  - `graduation_year` (optional, int): Graduation batch or `All`
  - `status` (optional, string): Offer status (`Placed`, `Offer Accepted`, etc.)
  - `company_id` (optional, int): Recruiting company ID or `All`
- **Response Format:** `application/json`

**Example Request:**
```http
GET /api/stats?department=Computer%20Science%20and%20Engineering&graduation_year=2026 HTTP/1.1
```

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
    "avg_package": 17.67,
    "highest_package": 32.5,
    "lowest_package": 3.8,
    "median_package": 17.75,
    "placement_rate": 100.0,
    "sample_label": "Synthetic Demonstration Data",
    "total_companies": 7,
    "total_eligible": 7,
    "total_placed": 7,
    "total_students": 8,
    "unplaced_students": 0
  },
  "success": true
}
```

---

#### 2.3 Dynamic Matplotlib Chart Streaming
Generates and streams headless, server-rendered Matplotlib visualizations as binary PNG images.

- **URL:** `/api/charts/<chart_name>`
- **Method:** `GET`
- **Supported `chart_name` Paths:**
  - `dept-rate`: Department-Wise Placement Rate (%) Bar Chart
  - `placed-vs-eligible`: Placed vs Eligible Students Grouped Bar Chart
  - `package-distribution`: Salary Package Distribution Histogram with Mean & Median
  - `top-skills`: Skills Most Frequently Recorded Among Placed Students
  - `company-recruitment`: Top Recruiting Companies & Average CTC
  - `yearly-trends`: Placement Rate & Average CTC Progression Line Chart
- **Query Parameters:**
  - `department` (optional, string)
  - `graduation_year` (optional, int)
- **Response Format:** `image/png`
- **Status Codes:**
  - `200 OK` (Image bytes returned)
  - `404 Not Found` (Invalid chart name)

---

#### 2.4 Reports CSV Export
Generates on-the-fly downloadable CSV files for academic evaluation.

- **URL:** `/reports/export-csv`
- **Method:** `GET`
- **Query Parameters:**
  - `type` (required, string): `summary`, `department`, `students`, `companies`, `packages`, `skills`
  - `department` (optional, string)
  - `graduation_year` (optional, int)
- **Response Format:** `text/csv`
- **Header:** `Content-Disposition: attachment; filename="placement_<type>_report_<timestamp>.csv"`

---

#### 2.5 CSV Sample Templates
Downloads valid sample CSV templates formatted with required columns.

- **URL:** `/import/template/<template_type>`
- **Method:** `GET`
- **Supported `template_type`:**
  - `students`: Generates `students_template.csv`
  - `placements`: Generates `placements_template.csv`
- **Response Format:** `text/csv`
