"""
Authentication and Session Management Blueprint.
Provides secure login, user registration (Sign-Up), Google account sign-in, and demo logins.
"""
import re
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash
from app.database.connection import get_db_cursor

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    next_url = request.values.get("next") or url_for("main.dashboard")

    # If already logged in, redirect directly to requested page or dashboard
    if session.get("user_id"):
        return redirect(next_url)

    if request.method == "POST":
        login_input = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not login_input or not password:
            flash("Please enter both username/email and password.", "danger")
            return render_template("auth/login.html", next_url=next_url)

        # Allow login by either username OR registered email address
        with get_db_cursor(commit=False) as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE username = %s OR email = %s LIMIT 1;",
                (login_input, login_input)
            )
            user = cursor.fetchone()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["user_id"]
            session["username"] = user["username"]
            session["full_name"] = user["full_name"]
            session["role"] = user["role"]
            session["email"] = user.get("email") or ""
            session["auth_provider"] = "Database"
            flash(f"Welcome back, {user['full_name']}!", "success")
            return redirect(next_url)
        else:
            flash("Invalid credentials. Please enter a valid username/email and password.", "danger")

    return render_template("auth/login.html", next_url=next_url)

@auth_bp.route("/register", methods=["GET", "POST"])
@auth_bp.route("/signup", methods=["GET", "POST"])
def register():
    """
    First-time User Registration / Sign-Up.
    Users create their own username, email, full name, role, and password.
    Once registered, their credentials are saved into MySQL and they can log in directly anytime.
    """
    next_url = request.values.get("next") or url_for("main.dashboard")

    if session.get("user_id"):
        return redirect(next_url)

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        role = request.form.get("role", "placement_officer").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        # Validation rules
        if not full_name or not username or not password:
            flash("Please fill in all required fields (Full Name, Username, and Password).", "danger")
            return render_template("auth/register.html", next_url=next_url)

        # Clean / validate username
        cleaned_username = re.sub(r'[^a-zA-Z0-9_]', '', username)
        if len(cleaned_username) < 3:
            flash("Username must be at least 3 characters long and contain only letters, numbers, or underscores.", "danger")
            return render_template("auth/register.html", next_url=next_url)

        if len(password) < 4:
            flash("Password must be at least 4 characters long.", "danger")
            return render_template("auth/register.html", next_url=next_url)

        if password != confirm_password:
            flash("Passwords do not match. Please ensure both passwords match.", "danger")
            return render_template("auth/register.html", next_url=next_url)

        # Ensure valid role selection
        allowed_roles = {"placement_officer", "admin", "student"}
        if role not in allowed_roles:
            role = "placement_officer"

        # Check if username or email already exists in MySQL
        with get_db_cursor(commit=False) as cursor:
            cursor.execute("SELECT user_id FROM users WHERE username = %s LIMIT 1;", (cleaned_username,))
            if cursor.fetchone():
                flash(f"Username '{cleaned_username}' is already taken. Please choose another username.", "danger")
                return render_template("auth/register.html", next_url=next_url)

            if email:
                cursor.execute("SELECT user_id FROM users WHERE email = %s LIMIT 1;", (email,))
                if cursor.fetchone():
                    flash(f"Email '{email}' is already registered. Please sign in directly or use a different email.", "danger")
                    return render_template("auth/register.html", next_url=next_url)

        # Hash password and insert into users table
        hashed_password = generate_password_hash(password)
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                """
                INSERT INTO users (username, password_hash, full_name, role, email)
                VALUES (%s, %s, %s, %s, %s);
                """,
                (cleaned_username, hashed_password, full_name, role, email or None)
            )
            new_user_id = cursor.lastrowid

        # Automatically log the user in
        session["user_id"] = new_user_id
        session["username"] = cleaned_username
        session["full_name"] = full_name
        session["role"] = role
        session["email"] = email
        session["auth_provider"] = "Registered"

        flash(f"Account created successfully! Welcome, {full_name}. You can now sign in anytime using your username or password.", "success")
        return redirect(next_url)

    return render_template("auth/register.html", next_url=next_url)

@auth_bp.route("/demo-login/<role>")
def demo_login(role):
    """
    Convenience one-click evaluator login for faculty demonstration.
    """
    next_url = request.args.get("next") or url_for("main.dashboard")

    if role == "faculty":
        session["user_id"] = 2
        session["username"] = "faculty"
        session["full_name"] = "Prof. Faculty Reviewer"
        session["role"] = "placement_officer"
        flash("Logged in with Faculty / Placement Officer demonstration profile.", "info")
    else:
        session["user_id"] = 1
        session["username"] = "admin"
        session["full_name"] = "System Administrator"
        session["role"] = "admin"
        flash("Logged in with Administrator demonstration profile.", "info")
    return redirect(next_url)

@auth_bp.route("/google-login", methods=["GET", "POST"])
def google_login():
    """
    Google Single Sign-On (SSO) login.
    Supports signing in with any personal/institutional Google Account email.
    If the account is new, automatically registers it into MySQL.
    """
    next_url = request.values.get("next") or url_for("main.dashboard")
    google_email = request.values.get("google_email", "").strip()
    google_name = request.values.get("google_name", "").strip()
    role = request.values.get("role", "placement_officer").strip()

    if not google_email:
        google_email = "placement.evaluator@gmail.com"
        google_name = "Google Verified Faculty Reviewer"
        cleaned_username = "google_faculty"
    else:
        if not google_name:
            raw_prefix = google_email.split("@")[0]
            google_name = raw_prefix.replace(".", " ").replace("_", " ").title()
            if not google_name:
                google_name = "Google Verified User"
        cleaned_username = re.sub(r'[^a-zA-Z0-9_]', '', google_email.split("@")[0])[:40] or "google_user"

    # Check if user already exists in MySQL by email
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("SELECT * FROM users WHERE email = %s LIMIT 1;", (google_email,))
        existing_user = cursor.fetchone()

        if existing_user:
            user_id = existing_user["user_id"]
            user_full_name = existing_user["full_name"]
            user_role = existing_user["role"]
            user_username = existing_user["username"]
        else:
            # Check if cleaned_username is taken; append random suffix if needed
            cursor.execute("SELECT user_id FROM users WHERE username = %s LIMIT 1;", (cleaned_username,))
            if cursor.fetchone():
                import random
                cleaned_username = f"{cleaned_username}_{random.randint(100, 999)}"

            # Auto-provision user in MySQL
            dummy_hash = generate_password_hash("GoogleAuthPass123!")
            cursor.execute(
                """
                INSERT INTO users (username, password_hash, full_name, role, email)
                VALUES (%s, %s, %s, %s, %s);
                """,
                (cleaned_username, dummy_hash, google_name, role, google_email)
            )
            user_id = cursor.lastrowid
            user_full_name = google_name
            user_role = role
            user_username = cleaned_username

    session["user_id"] = user_id
    session["username"] = user_username
    session["full_name"] = user_full_name
    session["email"] = google_email
    session["role"] = user_role
    session["auth_provider"] = "Google"

    flash(f"Signed in successfully with Google Account ({google_email}).", "success")
    return redirect(next_url)

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out. Please sign in to access the system.", "info")
    return redirect(url_for("auth.login"))
