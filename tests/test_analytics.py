"""
Unit tests for Placement Rate Formulas, Pandas/NumPy statistics, and edge cases.
"""
import pytest
import numpy as np
import pandas as pd
from app.services.analytics_service import (
    get_kpis,
    get_department_analytics,
    get_package_analytics,
    get_skill_analytics,
    get_yearly_trends
)

def test_kpi_calculations_and_formulas():
    """Verify primary analytics formulas and bounds."""
    kpis = get_kpis()
    assert kpis["total_students"] > 0
    assert kpis["total_eligible"] > 0
    assert kpis["total_placed"] <= kpis["total_eligible"]
    assert kpis["unplaced_students"] == (kpis["total_eligible"] - kpis["total_placed"])
    assert kpis["unplaced_students"] >= 0

    # Placement rate formula: (placed / eligible) * 100
    expected_rate = round((kpis["total_placed"] / kpis["total_eligible"]) * 100, 2)
    assert kpis["placement_rate"] == expected_rate
    assert 0.0 <= kpis["placement_rate"] <= 100.0

    # Package sanity
    assert kpis["avg_package"] > 0
    assert kpis["median_package"] > 0
    assert kpis["lowest_package"] <= kpis["highest_package"]

def test_empty_dataset_edge_cases():
    """Verify handling when filters yield zero records (no division by zero)."""
    # Non-existent department and year
    kpis = get_kpis(department="NonExistentBranchXYZ", graduation_year=1990)
    assert kpis["total_students"] == 0
    assert kpis["total_eligible"] == 0
    assert kpis["total_placed"] == 0
    assert kpis["unplaced_students"] == 0
    assert kpis["placement_rate"] == 0.0
    assert kpis["avg_package"] == 0.0
    assert kpis["median_package"] == 0.0

def test_department_analytics():
    """Verify department grouping and individual placement rates."""
    depts = get_department_analytics()
    assert len(depts) > 0
    for d in depts:
        assert "department" in d
        assert d["eligible_students"] >= 0
        assert d["placed_students"] >= 0
        assert d["unplaced_students"] >= 0
        assert 0.0 <= d["placement_rate"] <= 100.0
        if d["eligible_students"] > 0:
            calc_rate = round((d["placed_students"] / d["eligible_students"]) * 100, 2)
            assert d["placement_rate"] == calc_rate

def test_package_percentiles_with_numpy():
    """Verify package statistics percentiles."""
    pkg = get_package_analytics()
    assert pkg["count"] > 0
    assert pkg["min"] <= pkg["p25"] <= pkg["median"] <= pkg["p75"] <= pkg["p90"] <= pkg["max"]
    assert "brackets" in pkg
    assert len(pkg["brackets"]) == 4

def test_skill_analytics():
    """Verify skills tracking among placed students."""
    skills = get_skill_analytics()
    assert len(skills) > 0
    for s in skills:
        assert "skill_name" in s
        assert s["total_students_with_skill"] >= s["placed_students_with_skill"]
