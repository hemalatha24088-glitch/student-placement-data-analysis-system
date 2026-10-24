"""
Role-Based Access Control (RBAC) and Authentication Decorators.
Enforces strict least-privilege security across all application endpoints.
"""

import re
from functools import wraps

from flask import abort, current_app, flash, redirect, request, session, url_for


def is_strong_password(pw):
    """
    Enforce security policy on password complexity:
    - Minimum 8 characters
    - At least one lowercase letter
    - At least one uppercase letter
    - At least one number or special symbol
    """
    if not pw or len(pw) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"[a-z]", pw):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r"[A-Z]", pw):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"\d", pw):
        return False, "Password must contain at least one digit (0-9)."
    return True, ""


def login_required(f):
    """
    Decorator requiring an active authenticated user session.
    Redirects unauthenticated visitors to /login with next redirection URL.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            if request.is_json:
                return {"error": "Authentication required", "status": 401}, 401
            next_url = request.url if request.path not in ("/", "/login") else url_for("main.dashboard")
            return redirect(url_for("auth.login", next=next_url))
        return f(*args, **kwargs)

    return decorated_function


def role_required(*allowed_roles):
    """
    Decorator restricting endpoint access to specific authorized roles.
    Allowed roles: 'admin', 'placement_officer', 'student'.
    Aborts with HTTP 403 Forbidden if user lacks required role.
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get("user_id"):
                if request.is_json:
                    return {"error": "Authentication required", "status": 401}, 401
                next_url = request.url if request.path not in ("/", "/login") else url_for("main.dashboard")
                return redirect(url_for("auth.login", next=next_url))

            user_role = session.get("role", "student")
            if user_role not in allowed_roles:
                current_app.logger.warning(
                    f"Forbidden access attempt: user '{session.get('username')}' (role: {user_role}) "
                    f"attempted to access {request.path} requiring {allowed_roles}"
                )
                abort(403)

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def student_self_or_staff_required(get_target_student_id_func=None):
    """
    Decorator allowing:
    - Officers and Admins: access any student record.
    - Students: access ONLY their own linked student profile.
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get("user_id"):
                return redirect(url_for("auth.login", next=request.url))

            user_role = session.get("role", "student")
            if user_role in ("admin", "placement_officer"):
                return f(*args, **kwargs)

            # User is a student: determine target student_id from kwargs or helper
            target_id = kwargs.get("student_id")
            if get_target_student_id_func and callable(get_target_student_id_func):
                target_id = get_target_student_id_func(*args, **kwargs)

            user_student_id = session.get("student_id")

            if target_id is not None and user_student_id is not None:
                if int(target_id) != int(user_student_id):
                    abort(403)
                return f(*args, **kwargs)

            # If student is not linked or attempting to access other profile
            abort(403)

        return decorated_function

    return decorator
