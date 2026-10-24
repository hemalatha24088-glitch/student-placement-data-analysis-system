"""
Lightweight Versioned SQL Migration Runner.
Executes pending SQL migrations in migrations/ directory idempotently.
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database.connection import get_db_cursor


def run_migrations():
    """Find and execute all unapplied SQL migration files in alphabetical order."""
    migrations_dir = Path(__file__).parent
    sql_files = sorted(migrations_dir.glob("*.sql"))

    if not sql_files:
        print("No SQL migration files found in migrations/.")
        return

    print("Checking database migration status...")

    with get_db_cursor(commit=True) as cursor:
        # Ensure schema_migrations table exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS `schema_migrations` (
                `version` VARCHAR(100) PRIMARY KEY,
                `applied_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)
        cursor.execute("SELECT `version` FROM `schema_migrations`;")
        applied = {row["version"] for row in cursor.fetchall()}

    applied_count = 0
    for file_path in sql_files:
        version_name = file_path.name
        if version_name in applied:
            continue

        print(f"Applying migration: {version_name}...")
        sql_content = file_path.read_text(encoding="utf-8")
        statements = [stmt.strip() for stmt in sql_content.split(";") if stmt.strip()]

        with get_db_cursor(commit=True) as cursor:
            for stmt in statements:
                try:
                    cursor.execute(stmt)
                except Exception as e:
                    err_code = getattr(e, "args", [None])[0]
                    if err_code in (1061, 1050) or "Duplicate key name" in str(e) or "already exists" in str(e).lower():
                        continue
                    raise e
            cursor.execute("INSERT INTO `schema_migrations` (`version`) VALUES (%s);", (version_name,))

        applied_count += 1
        print(f"  [OK] Successfully applied {version_name}")

    if applied_count == 0:
        print("Database schema is fully up-to-date. No pending migrations.")
    else:
        print(f"Migration completed successfully. Applied {applied_count} migrations.")


if __name__ == "__main__":
    run_migrations()
