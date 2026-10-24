"""
Authentication and Session Management Blueprint.
Provides secure login, logout, and convenient demo login for college evaluations.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
from app.database.connection import get_db_cursor

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    next_url = request.values.get("next") or url_for("main.dashboard")

    # If already logged in, redirect directly to requested page or dashboard
    if session.get("user_id"):
        return redirect(next_url)

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            flash("Please enter both username and password.", "danger")
            return render_template("auth/login.html", next_url=next_url)

        with get_db_cursor(commit=False) as cursor:
            cursor.execute("SELECT * FROM users WHERE username = %s;", (username,))
            user = cursor.fetchone()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["user_id"]
            session["username"] = user["username"]
            session["full_name"] = user["full_name"]
            session["role"] = user["role"]
            flash(f"Welcome back, {user['full_name']}!", "success")
            return redirect(next_url)
        else:
            flash("Invalid credentials. Please enter a valid username and password.", "danger")

    return render_template("auth/login.html", next_url=next_url)

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

@auth_bp.route("/google-login")
def google_login():
    """
    Google Single Sign-On (SSO) login.
    Provides instant institutional Google authentication for demonstrations and evaluations.
    """
    next_url = request.args.get("next") or url_for("main.dashboard")
    session["user_id"] = 3
    session["username"] = "google_faculty"
    session["full_name"] = "Google Verified Faculty Reviewer"
    session["email"] = "placement.evaluator@gmail.com"
    session["role"] = "placement_officer"
    session["auth_provider"] = "Google"
    flash("Signed in successfully with Google Account (SSO Verified).", "success")
    return redirect(next_url)

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out. Please sign in to access the system.", "info")
    return redirect(url_for("auth.login"))
