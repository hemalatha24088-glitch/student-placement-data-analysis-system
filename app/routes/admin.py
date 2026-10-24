"""
Administrator User Management Blueprint.
Enables role assignment, access level promotion, and account auditing.
"""

from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for
from werkzeug.security import generate_password_hash

from app.database.connection import get_db_cursor
from app.utils.auth import role_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/users")
@role_required("admin")
def list_users():
    """List all registered users with role and status details."""
    with get_db_cursor(commit=False) as cursor:
        cursor.execute("""
            SELECT user_id, username, full_name, role, email, created_at 
            FROM users 
            ORDER BY created_at DESC;
            """)
        users = cursor.fetchall()

    return render_template("admin/users.html", users=users)


@admin_bp.route("/users/<int:user_id>/role", methods=["POST"])
@role_required("admin")
def update_user_role(user_id):
    """Promote or change a user's role (admin, placement_officer, student)."""
    new_role = request.form.get("role", "").strip()
    valid_roles = {"admin", "placement_officer", "student"}

    if new_role not in valid_roles:
        flash("Invalid role specified.", "danger")
        return redirect(url_for("admin.list_users"))

    # Prevent admin from demoting their own current active session
    if user_id == session.get("user_id") and new_role != "admin":
        flash("Action blocked: You cannot demote your own administrator account.", "warning")
        return redirect(url_for("admin.list_users"))

    with get_db_cursor(commit=True) as cursor:
        cursor.execute("SELECT username, full_name FROM users WHERE user_id = %s;", (user_id,))
        user = cursor.fetchone()
        if not user:
            flash("User not found.", "danger")
            return redirect(url_for("admin.list_users"))

        cursor.execute("UPDATE users SET role = %s WHERE user_id = %s;", (new_role, user_id))
        flash(f"User '{user['username']}' role updated to '{new_role}'.", "success")

    return redirect(url_for("admin.list_users"))


@admin_bp.route("/users/<int:user_id>/reset-password", methods=["POST"])
@role_required("admin")
def reset_user_password(user_id):
    """Admin-initiated password reset."""
    new_password = request.form.get("new_password", "").strip()

    if len(new_password) < 8:
        flash("Password must be at least 8 characters long.", "danger")
        return redirect(url_for("admin.list_users"))

    hashed_pw = generate_password_hash(new_password)

    with get_db_cursor(commit=True) as cursor:
        cursor.execute("SELECT username FROM users WHERE user_id = %s;", (user_id,))
        user = cursor.fetchone()
        if not user:
            flash("User not found.", "danger")
            return redirect(url_for("admin.list_users"))

        cursor.execute("UPDATE users SET password_hash = %s WHERE user_id = %s;", (hashed_pw, user_id))
        flash(f"Password reset successfully for user '{user['username']}'.", "success")

    return redirect(url_for("admin.list_users"))


@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@role_required("admin")
def delete_user(user_id):
    """Delete a user account."""
    if user_id == session.get("user_id"):
        flash("Action blocked: You cannot delete your own active administrator account.", "danger")
        return redirect(url_for("admin.list_users"))

    with get_db_cursor(commit=True) as cursor:
        cursor.execute("SELECT username FROM users WHERE user_id = %s;", (user_id,))
        user = cursor.fetchone()
        if not user:
            flash("User not found.", "warning")
            return redirect(url_for("admin.list_users"))

        cursor.execute("DELETE FROM users WHERE user_id = %s;", (user_id,))
        flash(f"User '{user['username']}' has been permanently deleted.", "info")

    return redirect(url_for("admin.list_users"))
