"""
Unit tests for MySQL database connectivity and health monitoring.
"""

import pytest

from app.database.connection import check_db_health, get_db_connection, get_db_cursor


def test_database_connection():
    """Verify that a direct connection to MySQL 8.0 can be established."""
    conn = get_db_connection()
    assert conn is not None
    cursor = conn.cursor()
    cursor.execute("SELECT 1 AS alive;")
    res = cursor.fetchone()
    assert res["alive"] == 1
    cursor.close()
    conn.close()


def test_health_check_endpoint():
    """Verify that check_db_health reports healthy and returns valid table counts."""
    health = check_db_health()
    assert health["status"] == "healthy"
    assert health["connected"] is True
    assert "8.0" in health["server_version"]
    assert health["database_name"] == "placement_db"
    assert health["tables"]["students"] > 0
    assert health["tables"]["placements"] > 0
    assert health["tables"]["companies"] > 0
    assert health["tables"]["skills"] > 0
