"""
Database initialization script for Student Placement Data Analysis System.
Executes schema.sql and seed.sql against MySQL 8.0 server.
"""
import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3307))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "aimlb4")
DB_NAME = os.getenv("DB_NAME", "placement_db")

def execute_sql_file(conn, file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        sql_content = f.read()

    # Split on semicolon, ignoring blank lines and comments
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

def init_database():
    print(f"Connecting to MySQL server at {DB_HOST}:{DB_PORT} as {DB_USER}...")
    conn = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        autocommit=True
    )
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

    print("Seeding synthetic initial data from seed.sql...")
    execute_sql_file(conn, seed_path)
    print("Seed data applied successfully.")

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
    init_database()
