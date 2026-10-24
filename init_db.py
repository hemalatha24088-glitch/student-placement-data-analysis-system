"""
Database initialization and management script for Student Placement Data Analysis System.
Provides idempotent schema execution, seed data loading, admin creation, and large dataset generation.
"""
import os
import sys
import argparse
import getpass
import pymysql
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
db_port_val = os.getenv("DB_PORT", "3307").strip()
DB_PORT = int(db_port_val) if db_port_val.isdigit() else 3307
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME", "placement_db")
DB_SSL = os.getenv("DB_SSL", "False").lower() in ("true", "1", "yes")

if DB_PASSWORD is None:
    raise RuntimeError(
        "FATAL: Missing required environment variable 'DB_PASSWORD'. "
        "Define DB_PASSWORD in your .env file or environment before running init_db.py."
    )

def get_connection(use_database=True):
    conn_params = {
        "host": DB_HOST,
        "port": DB_PORT,
        "user": DB_USER,
        "password": DB_PASSWORD,
        "autocommit": True,
        "charset": "utf8mb4"
    }
    if use_database:
        conn_params["database"] = DB_NAME
    if DB_SSL:
        conn_params["ssl"] = {"ssl": True}
    return pymysql.connect(**conn_params)

def execute_sql_file(conn, file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        sql_content = f.read()

    statements = []
    current_stmt = []
    for line in sql_content.splitlines():
        trimmed = line.strip()
        if trimmed.startswith("--") or not trimmed:
            continue
        current_stmt.append(line)
        if trimmed.endswith(";"):
            statements.append("\n".join(current_stmt))
            current_stmt = []
    if current_stmt:
        remaining = "\n".join(current_stmt).strip()
        if remaining:
            statements.append(remaining)

    cursor = conn.cursor()
    for stmt in statements:
        s = stmt.strip()
        if s:
            cursor.execute(s)
    cursor.close()

def create_admin_user(username=None, password=None, email=None, full_name=None):
    """Create or update an administrator account safely."""
    username = username or os.getenv("ADMIN_USERNAME")
    if not username:
        if sys.stdin.isatty():
            username = input("Enter administrator username [admin]: ").strip() or "admin"
        else:
            username = "admin"

    password = password or os.getenv("ADMIN_PASSWORD")
    if not password:
        if sys.stdin.isatty():
            password = getpass.getpass("Enter administrator password (min 8 chars): ")
        else:
            raise ValueError("ADMIN_PASSWORD must be provided via environment in non-interactive sessions.")

    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long.")

    email = email or os.getenv("ADMIN_EMAIL", f"{username}@placement.edu")
    full_name = full_name or os.getenv("ADMIN_FULL_NAME", "System Administrator")

    hashed_pw = generate_password_hash(password)

    conn = get_connection(use_database=True)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE username = %s;", (username,))
    existing = cursor.fetchone()

    if existing:
        cursor.execute(
            """
            UPDATE users 
            SET password_hash = %s, full_name = %s, role = 'admin', email = %s 
            WHERE username = %s;
            """,
            (hashed_pw, full_name, email, username)
        )
        print(f"[OK] Administrator '{username}' credentials updated successfully.")
    else:
        cursor.execute(
            """
            INSERT INTO users (username, password_hash, full_name, role, email)
            VALUES (%s, %s, %s, 'admin', %s);
            """,
            (username, hashed_pw, full_name, email)
        )
        print(f"[OK] Administrator '{username}' created successfully.")

    cursor.close()
    conn.close()

def seed_demo_accounts():
    """Seed demo accounts only when DEMO_MODE is explicitly enabled."""
    demo_flag = os.getenv("DEMO_MODE", "False").lower() in ("true", "1", "yes")
    if not demo_flag:
        print("[INFO] DEMO_MODE is not active. Skipping demonstration accounts.")
        return

    conn = get_connection(use_database=True)
    cursor = conn.cursor()

    demo_faculty_pw = generate_password_hash(os.getenv("DEMO_FACULTY_PASSWORD", "DemoFaculty@2026"))
    demo_admin_pw = generate_password_hash(os.getenv("DEMO_ADMIN_PASSWORD", "DemoAdmin@2026"))

    # Update or insert faculty demo
    cursor.execute("SELECT user_id FROM users WHERE username = 'faculty';")
    if cursor.fetchone():
        cursor.execute("UPDATE users SET password_hash = %s WHERE username = 'faculty';", (demo_faculty_pw,))
    else:
        cursor.execute(
            """
            INSERT INTO users (username, password_hash, full_name, role, email)
            VALUES ('faculty', %s, 'Prof. Faculty Reviewer (Demo)', 'placement_officer', 'faculty.demo@placement.edu');
            """,
            (demo_faculty_pw,)
        )

    # Update or insert admin demo
    cursor.execute("SELECT user_id FROM users WHERE username = 'admin';")
    if cursor.fetchone():
        cursor.execute("UPDATE users SET password_hash = %s WHERE username = 'admin';", (demo_admin_pw,))
    else:
        cursor.execute(
            """
            INSERT INTO users (username, password_hash, full_name, role, email)
            VALUES ('admin', %s, 'System Administrator (Demo)', 'admin', 'admin.demo@placement.edu');
            """,
            (demo_admin_pw,)
        )

    cursor.close()
    conn.close()
    print("[OK] Demo mode accounts initialized with environment-secured credentials.")

def init_database():
    print(f"Connecting to MySQL server at {DB_HOST}:{DB_PORT} as {DB_USER}...")
    conn = get_connection(use_database=False)
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    cursor.execute(f"USE `{DB_NAME}`;")
    print(f"Database `{DB_NAME}` ready.")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    schema_path = os.path.join(base_dir, "schema.sql")
    seed_path = os.path.join(base_dir, "seed.sql")

    print("Applying schema.sql...")
    execute_sql_file(conn, schema_path)
    print("Schema applied successfully.")

    print("Seeding initial dataset from seed.sql...")
    execute_sql_file(conn, seed_path)
    print("Seed data applied successfully.")

    # Check if demo mode accounts should be seeded
    seed_demo_accounts()

    # Verification query
    cursor = conn.cursor()
    tables = ["students", "skills", "student_skills", "companies", "placements", "users"]
    print("\n--- DATABASE VERIFICATION SUMMARY ---")
    for t in tables:
        cursor.execute(f"SELECT COUNT(*) FROM `{t}`;")
        count = cursor.fetchone()[0]
        print(f" Table '{t}': {count} records")

    cursor.close()
    conn.close()
    print("\n[SUCCESS] Placement Database fully initialized and ready!\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize and manage the placement system database.")
    parser.add_argument("--create-admin", action="store_true", help="Interactively create or update an administrator account.")
    parser.add_argument("--seed-demo", action="store_true", help="Seed demo accounts (requires DEMO_MODE=true).")
    parser.add_argument("--large-seed", action="store_true", help="Seed a large dataset (500-1000 realistic records).")
    args = parser.parse_args()

    if args.create_admin:
        create_admin_user()
    elif args.seed_demo:
        seed_demo_accounts()
    elif args.large_seed:
        # Phase 3 feature hook: will be implemented in Phase 3
        from app.services.large_seed_service import generate_large_dataset
        generate_large_dataset()
    else:
        init_database()
