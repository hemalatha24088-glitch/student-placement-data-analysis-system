"""
Database Connection Manager for Student Placement Data Analysis System.
Provides thread-safe connections, DictCursor contexts, and connectivity diagnostics.
"""
import pymysql
import pymysql.cursors
from contextlib import contextmanager
from flask import current_app, g
from config import Config

def get_db_connection():
    """Create and return a new MySQL connection with DictCursor."""
    conn_kwargs = {
        "host": Config.DB_HOST,
        "port": Config.DB_PORT,
        "user": Config.DB_USER,
        "password": Config.DB_PASSWORD,
        "database": Config.DB_NAME,
        "charset": "utf8mb4",
        "cursorclass": pymysql.cursors.DictCursor,
        "autocommit": False
    }
    if getattr(Config, "DB_SSL", False):
        conn_kwargs["ssl"] = {"ssl": True}
    return pymysql.connect(**conn_kwargs)

@contextmanager
def get_db_cursor(commit=True):
    """
    Context manager that yields a database cursor.
    Automatically commits on normal exit, rolls back on exception,
    and reliably closes the connection.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        yield cursor
        if commit:
            conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def execute_query(query, params=None, fetchone=False, fetchall=False, commit=False):
    """Convenience helper to run parameterized queries safely."""
    with get_db_cursor(commit=commit) as cursor:
        cursor.execute(query, params or ())
        if fetchone:
            return cursor.fetchone()
        if fetchall:
            return cursor.fetchall()
        return cursor.lastrowid

def check_db_health():
    """
    Diagnostic health check function that verifies database connectivity,
    server version, and record counts across primary tables.
    """
    try:
        with get_db_cursor(commit=False) as cursor:
            cursor.execute("SELECT VERSION() AS version, DATABASE() AS database_name;")
            meta = cursor.fetchone()

            cursor.execute("SELECT COUNT(*) AS count FROM students;")
            students_count = cursor.fetchone()["count"]

            cursor.execute("SELECT COUNT(*) AS count FROM placements;")
            placements_count = cursor.fetchone()["count"]

            cursor.execute("SELECT COUNT(*) AS count FROM companies;")
            companies_count = cursor.fetchone()["count"]

            cursor.execute("SELECT COUNT(*) AS count FROM skills;")
            skills_count = cursor.fetchone()["count"]

            return {
                "status": "healthy",
                "connected": True,
                "server_version": meta["version"],
                "database_name": meta["database_name"],
                "tables": {
                    "students": students_count,
                    "placements": placements_count,
                    "companies": companies_count,
                    "skills": skills_count
                }
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "connected": False,
            "error": str(e)
        }
