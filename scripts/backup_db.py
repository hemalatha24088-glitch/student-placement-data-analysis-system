"""
Automated Database Backup Utility.
Exports full MySQL database schema and data to timestamped SQL dump files.
Supports native mysqldump executable with intelligent Python fallback.
"""

import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database.connection import get_db_cursor
from config import Config


def generate_python_fallback_dump(dump_file_path):
    """Pure-Python dump fallback when mysqldump is not in system PATH."""
    tables = ["schema_migrations", "users", "students", "companies", "skills", "placements", "student_skills"]

    with open(dump_file_path, "w", encoding="utf-8") as f:
        f.write("-- Student Placement Data Analysis System\n")
        f.write("-- Automated Database Backup Dump\n")
        f.write(f"-- Generated At: {datetime.now().isoformat()}\n")
        f.write(f"-- Database: {Config.DB_NAME}\n\n")
        f.write("SET FOREIGN_KEY_CHECKS = 0;\n\n")

        with get_db_cursor(commit=False) as cursor:
            for table in tables:
                cursor.execute(f"SHOW TABLES LIKE '{table}';")
                if not cursor.fetchone():
                    continue

                # Dump CREATE TABLE
                cursor.execute(f"SHOW CREATE TABLE `{table}`;")
                row = cursor.fetchone()
                create_sql = row.get("Create Table") or row.get("create table") or list(row.values())[1]
                f.write(f"DROP TABLE IF EXISTS `{table}`;\n")
                f.write(f"{create_sql};\n\n")

                # Dump Rows
                cursor.execute(f"SELECT * FROM `{table}`;")
                records = cursor.fetchall()
                if records:
                    columns = list(records[0].keys())
                    cols_str = ", ".join([f"`{c}`" for c in columns])
                    f.write(f"INSERT INTO `{table}` ({cols_str}) VALUES\n")

                    values_list = []
                    for r in records:
                        row_vals = []
                        for col in columns:
                            val = r[col]
                            if val is None:
                                row_vals.append("NULL")
                            elif isinstance(val, (int, float)):
                                row_vals.append(str(val))
                            else:
                                escaped = str(val).replace("\\", "\\\\").replace("'", "\\'")
                                row_vals.append(f"'{escaped}'")
                        values_list.append(f"({', '.join(row_vals)})")

                    f.write(",\n".join(values_list) + ";\n\n")

        f.write("SET FOREIGN_KEY_CHECKS = 1;\n")
        f.write("-- Backup Completed Successfully.\n")


def backup_database(output_dir="backups", max_backups=10):
    """Execute database backup and rotate old backup files."""
    out_path = Path(output_dir)
    out_path.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"placement_db_backup_{timestamp}.sql"
    backup_file = out_path / backup_filename

    print(f"Initiating database backup for '{Config.DB_NAME}' on {Config.DB_HOST}:{Config.DB_PORT}...")

    mysqldump_bin = shutil.which("mysqldump")
    used_tool = "mysqldump"

    if mysqldump_bin:
        cmd = [
            mysqldump_bin,
            f"--host={Config.DB_HOST}",
            f"--port={Config.DB_PORT}",
            f"--user={Config.DB_USER}",
            f"--password={Config.DB_PASSWORD}",
            "--single-transaction",
            "--quick",
            "--routines",
            "--triggers",
            Config.DB_NAME,
        ]
        try:
            with open(backup_file, "w", encoding="utf-8") as f:
                subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True, check=True)
        except Exception as e:
            print(f"Warning: mysqldump execution failed: {str(e)}. Switching to internal Python fallback...")
            generate_python_fallback_dump(backup_file)
            used_tool = "python_db_dumper (fallback)"
    else:
        generate_python_fallback_dump(backup_file)
        used_tool = "python_db_dumper"

    size_kb = backup_file.stat().st_size / 1024
    print(f"[OK] Database backup created successfully via {used_tool}!")
    print(f"     Destination: {backup_file}")
    print(f"     File Size:   {size_kb:.2f} KB")

    # Rotate old backups
    existing = sorted(out_path.glob("placement_db_backup_*.sql"))
    if len(existing) > max_backups:
        to_delete = existing[:-max_backups]
        for old in to_delete:
            old.unlink()
            print(f"     Rotated out older backup: {old.name}")

    return str(backup_file)


if __name__ == "__main__":
    backup_database()
