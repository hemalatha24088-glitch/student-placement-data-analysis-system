"""
Authentication and Session Management Blueprint.
Provides secure login, Student-only registration, genuine Google OAuth 2.0, and password management.
"""

import re

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from app.database.connection import get_db_cursor
from app.limiter import limiter
from app.utils.auth import is_strong_password, login_required

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute", methods=["POST"])
def login():
    """
    Standard secure user login.
    Supports login via Username OR registered Email.
    Returns generic error messages to prevent username enumeration.
    """
    next_url = request.values.get("next") or url_for("main.dashboard")

    if session.get("user_id"):
        return redirect(next_url)

    if request.method == "POST":
        login_input = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not login_input or not password:
            flash("Invalid credentials. Please verify your details.", "danger")
            return render_template("auth/login.html", next_url=next_url)

        with get_db_cursor(commit=False) as cursor:
            cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s LIMIT 1;", (login_input, login_input))
            user = cursor.fetchone()

        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session.permanent = True
            session["user_id"] = user["user_id"]
            session["username"] = user["username"]
            session["full_name"] = user["full_name"]
            session["role"] = user["role"]
            session["email"] = user.get("email") or ""

            # If user is a student, link student_id if available
            if user["role"] == "student":
                with get_db_cursor(commit=False) as s_cur:
                    s_cur.execute(
                        "SELECT student_id FROM students WHERE email = %s OR roll_no = %s LIMIT 1;",
                        (user.get("email"), user["username"]),
                    )
                    st = s_cur.fetchone()
                    if st:
                        session["student_id"] = st["student_id"]

            flash(f"Welcome back, {user['full_name']}!", "success")
            return redirect(next_url)
        else:
            # Generic message prevents account existence enumeration
            flash("Invalid credentials. Please verify your details.", "danger")

    return render_template("auth/login.html", next_url=next_url)


@auth_bp.route("/register", methods=["GET", "POST"])
@auth_bp.route("/signup", methods=["GET", "POST"])
@limiter.limit("5 per minute", methods=["POST"])
def register():
    """
    Public registration endpoint.
    Restricted strictly to creating 'Student' accounts.
    Administrative and placement officer roles require administrator promotion.
    """
    next_url = request.values.get("next") or url_for("main.dashboard")

    if session.get("user_id"):
        return redirect(next_url)

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        # Enforce Student role strictly
        role = "student"

        if not full_name or not username or not password:
            flash("Please fill in all required fields (Full Name, Username, and Password).", "danger")
            return render_template("auth/register.html", next_url=next_url)

        cleaned_username = re.sub(r"[^a-zA-Z0-9_]", "", username)
        if len(cleaned_username) < 3 or cleaned_username != username:
            flash(
                "Username must be at least 3 characters long and contain only letters, numbers, or underscores.",
                "danger",
            )
            return render_template("auth/register.html", next_url=next_url)

        # Password strength policy check
        is_strong, msg = is_strong_password(password)
        if not is_strong:
            flash(msg, "danger")
            return render_template("auth/register.html", next_url=next_url)

        if password != confirm_password:
            flash("Passwords do not match. Please re-enter your password.", "danger")
            return render_template("auth/register.html", next_url=next_url)

        with get_db_cursor(commit=False) as cursor:
            cursor.execute("SELECT user_id FROM users WHERE username = %s LIMIT 1;", (cleaned_username,))
            if cursor.fetchone():
                flash("That username is already taken. Please choose another username.", "danger")
                return render_template("auth/register.html", next_url=next_url)

            if email:
                cursor.execute("SELECT user_id FROM users WHERE email = %s LIMIT 1;", (email,))
                if cursor.fetchone():
                    flash("An account with that email already exists. Please sign in directly.", "danger")
                    return render_template("auth/register.html", next_url=next_url)

        hashed_password = generate_password_hash(password)
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                """
                INSERT INTO users (username, password_hash, full_name, role, email)
                VALUES (%s, %s, %s, %s, %s);
                """,
                (cleaned_username, hashed_password, full_name, role, email or None),
            )
            new_user_id = cursor.lastrowid

        session.clear()
        session.permanent = True
        session["user_id"] = new_user_id
        session["username"] = cleaned_username
        session["full_name"] = full_name
        session["role"] = role
        session["email"] = email

        flash(f"Account successfully created! Welcome, {full_name}.", "success")
        return redirect(next_url)

    return render_template("auth/register.html", next_url=next_url)


@auth_bp.route("/change-password", methods=["GET", "POST"])
@auth_bp.route("/auth/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    """Allow authenticated users to update their own password."""
    if request.method == "POST":
        old_password = (request.form.get("old_password") or request.form.get("current_password") or "").strip()
        new_password = request.form.get("new_password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        if new_password != confirm_password:
            flash("New passwords do not match.", "danger")
            return render_template("auth/change_password.html")

        is_strong, msg = is_strong_password(new_password)
        if not is_strong:
            flash(msg, "danger")
            return render_template("auth/change_password.html")

        with get_db_cursor(commit=False) as cursor:
            cursor.execute("SELECT password_hash FROM users WHERE user_id = %s;", (session["user_id"],))
            user = cursor.fetchone()

        if not user or not check_password_hash(user["password_hash"], old_password):
            flash("Current password is incorrect.", "danger")
            return render_template("auth/change_password.html")

        hashed_pw = generate_password_hash(new_password)
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("UPDATE users SET password_hash = %s WHERE user_id = %s;", (hashed_pw, session["user_id"]))

        flash("Your password has been updated successfully.", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("auth/change_password.html")


@auth_bp.route("/login/google")
@auth_bp.route("/auth/google")
def google_login():
    """
    Real Google OAuth 2.0 authorization initiator.
    Hides/rejects if Google OAuth credentials are not configured.
    """
    from app import oauth

    if not current_app.config.get("GOOGLE_CLIENT_ID") or not current_app.config.get("GOOGLE_CLIENT_SECRET"):
        flash("Google Single Sign-On is not configured on this server.", "warning")
        return redirect(url_for("auth.login"))

    redirect_uri = url_for("auth.google_callback", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@auth_bp.route("/callback/google")
def google_callback():
    """Google OAuth 2.0 callback handler."""
    from app import oauth

    if not current_app.config.get("GOOGLE_CLIENT_ID"):
        abort(404)

    try:
        token = oauth.google.authorize_access_token()
        userinfo = token.get("userinfo") or oauth.google.userinfo()
        google_email = userinfo["email"]
        google_name = userinfo.get("name", google_email.split("@")[0])

        with get_db_cursor(commit=True) as cursor:
            cursor.execute("SELECT * FROM users WHERE email = %s LIMIT 1;", (google_email,))
            user = cursor.fetchone()

            if user:
                user_id = user["user_id"]
                user_role = user["role"]
                username = user["username"]
                full_name = user["full_name"]
            else:
                # New user from Google gets default 'student' role
                username = re.sub(r"[^a-zA-Z0-9_]", "", google_email.split("@")[0])[:40] or "google_user"
                cursor.execute("SELECT user_id FROM users WHERE username = %s LIMIT 1;", (username,))
                if cursor.fetchone():
                    import random

                    username = f"{username}_{random.randint(100, 999)}"

                dummy_hash = generate_password_hash("OAUTH_EXTERNAL_MANAGED")
                cursor.execute(
                    """
                    INSERT INTO users (username, password_hash, full_name, role, email)
                    VALUES (%s, %s, %s, 'student', %s);
                    """,
                    (username, dummy_hash, google_name, google_email),
                )
                user_id = cursor.lastrowid
                user_role = "student"
                full_name = google_name

        session.clear()
        session.permanent = True
        session["user_id"] = user_id
        session["username"] = username
        session["full_name"] = full_name
        session["email"] = google_email
        session["role"] = user_role
        session["auth_provider"] = "Google"

        flash(f"Signed in successfully via Google as {full_name}.", "success")
        return redirect(url_for("main.dashboard"))
    except Exception as e:
        current_app.logger.error(f"Google OAuth Callback Error: {str(e)}")
        flash("Google authentication could not be completed. Please try again.", "danger")
        return redirect(url_for("auth.login"))


@auth_bp.route("/demo-login/<role>")
def demo_login(role):
    """
    Convenience one-click demonstration login.
    Accessible ONLY when DEMO_MODE=true is explicitly configured.
    """
    if not current_app.config.get("DEMO_MODE"):
        flash("Demonstration mode is disabled on this system.", "warning")
        return redirect(url_for("auth.login"))

    next_url = request.args.get("next") or url_for("main.dashboard")

    if role == "faculty":
        session.clear()
        session.permanent = True
        session["user_id"] = 2
        session["username"] = "faculty"
        session["full_name"] = "Prof. Faculty Reviewer (Demo)"
        session["role"] = "placement_officer"
        flash("Logged in with Faculty Reviewer demo profile.", "info")
    elif role == "admin":
        session.clear()
        session.permanent = True
        session["user_id"] = 1
        session["username"] = "admin"
        session["full_name"] = "System Administrator (Demo)"
        session["role"] = "admin"
        flash("Logged in with Administrator demo profile.", "info")
    elif role == "student":
        session.clear()
        session.permanent = True
        session["user_id"] = 3
        session["username"] = "student_demo"
        session["full_name"] = "Demo Student Candidate"
        session["role"] = "student"
        session["student_id"] = 1
        flash("Logged in with Student demo profile.", "info")
    else:
        abort(404)

    return redirect(next_url)


@auth_bp.route("/logout")
def logout():
    """Clear session and sign out."""
    session.clear()
    flash("You have been signed out.", "info")
    return redirect(url_for("auth.login"))
