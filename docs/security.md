# Security Policy & Implementation Architecture

The **Student Placement Data Analysis System** is engineered with a **defense-in-depth security model** protecting academic, student, and institutional placement records against unauthorized modification, data exfiltration, injection attacks, and credential brute-forcing.

---

## 1. Role-Based Access Control (RBAC) Matrix

Access control is enforced at the route level via `@login_required`, `@role_required(*roles)`, and `@student_self_or_staff_required` decorators:

| Endpoint / Action | Anonymous | Student | Placement Officer | Administrator |
| :--- | :---: | :---: | :---: | :---: |
| `/login`, `/register`, `/health` | Allowed | Redirected | Redirected | Redirected |
| `/dashboard` | 302 Redirect | Allowed | Allowed | Allowed |
| `/predictor/`, `/predictor/salary` | 302 Redirect | Allowed | Allowed | Allowed |
| `/skills/recommender`, `/ats/` | 302 Redirect | Allowed | Allowed | Allowed |
| View Own Student Profile | 302 Redirect | **Own Only** | Allowed | Allowed |
| View Other Student Profile | 302 Redirect | **403 Forbidden** | Allowed | Allowed |
| Student Add / Edit / Delete | 302 Redirect | **403 Forbidden** | Allowed | Allowed |
| Company Add / Edit / Delete | 302 Redirect | **403 Forbidden** | Allowed | Allowed |
| Placement Records Management | 302 Redirect | **403 Forbidden** | Allowed | Allowed |
| CSV Data Import (`/import/`) | 302 Redirect | **403 Forbidden** | Allowed | Allowed |
| Summary Reports (`/reports/`) | 302 Redirect | **403 Forbidden** | Allowed | Allowed |
| Model Retraining (`/retrain`) | 302 Redirect | **403 Forbidden** | Allowed | Allowed |
| User Role Promotion / Demotion | 302 Redirect | **403 Forbidden** | **403 Forbidden** | **Allowed** |
| Admin Password Reset (`/admin/users`) | 302 Redirect | **403 Forbidden** | **403 Forbidden** | **Allowed** |

### Public Registration Integrity
Public sign-up (`/register`) is strictly constrained to creating `Student` accounts. The role parameter is hardcoded on submission—even if an attacker crafts a malicious POST request injecting `role=admin`, the server enforces `role = "student"`.

---

## 2. SQL Injection Prevention

Every database interaction throughout the repository executes parameterized SQL queries using PyMySQL parameter binding (`%s`). No string concatenation, f-strings, or raw interpolation are permitted in SQL queries.

```python
# Secure: Parameterized query binding
cursor.execute(
    "SELECT * FROM users WHERE username = %s OR email = %s LIMIT 1;",
    (login_input, login_input)
)
```

---

## 3. Universal CSRF Protection

Cross-Site Request Forgery (CSRF) protection is provided via `Flask-WTF`. All state-altering operations (form submissions, file uploads, role promotions, account modifications, and model retraining) require a valid CSRF token. Destructive actions (deletions) strictly enforce `POST` methods—`GET` requests cannot delete records.

---

## 4. Rate Limiting & Anti-Brute-Force

Authentication endpoints are protected by `Flask-Limiter` with an in-memory or Redis-backed storage engine:
- `/login`: 5 requests per minute per remote IP.
- `/register`: 5 requests per minute per remote IP.
- Invalid credentials return a generic error message: *"Invalid credentials. Please verify your details."* to prevent username enumeration.

---

## 5. CSV & Formula Injection Hardening

During CSV imports and exports:
1. **Filename Sanitization:** Uploaded filenames are sanitized using `werkzeug.utils.secure_filename`.
2. **File Size Limit:** Capped at 5 MB maximum file size.
3. **Row Count Cap:** Maximum 1,000 rows processed per batch.
4. **Formula Injection Sanitization:** During CSV export, any cell beginning with `=`, `+`, `-`, `@`, `\t`, or `\r` is automatically prefixed with a single quote (`'`) via `sanitize_csv_cell()` to prevent formula execution in spreadsheet applications (e.g. Microsoft Excel, LibreOffice Calc).

---

## 6. Password Policy & Cryptography

- Minimum 8 characters in length.
- Must contain at least one uppercase letter, one lowercase letter, and one numerical digit.
- Password hashing is executed using `werkzeug.security.generate_password_hash` with secure salting. Plaintext passwords are never stored.

---

## 7. Security Headers & Session Cookies

Configured via `flask-talisman`:
- **Content-Security-Policy (CSP):** Restricts script, style, and font loading to authorized origins and self.
- **X-Content-Type-Options:** `nosniff` prevents MIME-type sniffing.
- **X-Frame-Options:** `SAMEORIGIN` mitigates clickjacking.
- **Referrer-Policy:** `strict-origin-when-cross-origin`.
- **Session Cookies:** `SESSION_COOKIE_HTTPONLY=True`, `SESSION_COOKIE_SAMESITE="Lax"`, `SESSION_COOKIE_SECURE=True` in production.

---

## 8. Honest OAuth 2.0 Integration

The *"Sign in with Google"* option uses genuine OAuth 2.0 (`Authlib`). If `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are not set in the environment, the Google Sign-In button is **hidden completely** from the interface. No mock or fake Google authentication is ever displayed.

---

## 9. Zero Leaked Stack Traces

Custom error pages (`403.html`, `404.html`, `429.html`, `500.html`) provide clean, user-friendly notices without leaking database schema details, stack traces, or environment paths.
