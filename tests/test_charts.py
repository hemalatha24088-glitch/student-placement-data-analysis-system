"""
Unit tests for Matplotlib visual generation service.
"""
import pytest
from app.services.chart_service import (
    generate_dept_placement_rate_chart,
    generate_placed_vs_eligible_chart,
    generate_package_distribution_chart,
    generate_top_skills_chart,
    generate_company_recruitment_chart,
    generate_yearly_trends_chart
)

def test_all_six_charts_generation():
    """Verify that all six Matplotlib chart generators produce valid PNG bytes."""
    chart1 = generate_dept_placement_rate_chart()
    chart2 = generate_placed_vs_eligible_chart()
    chart3 = generate_package_distribution_chart()
    chart4 = generate_top_skills_chart()
    chart5 = generate_company_recruitment_chart()
    chart6 = generate_yearly_trends_chart()

    for i, c in enumerate([chart1, chart2, chart3, chart4, chart5, chart6], start=1):
        assert isinstance(c, bytes), f"Chart {i} did not return bytes"
        assert len(c) > 1000, f"Chart {i} output was suspiciously small: {len(c)} bytes"
        # Standard PNG magic number: \x89PNG\r\n\x1a\n
        assert c.startswith(b"\x89PNG\r\n\x1a\n"), f"Chart {i} lacks PNG magic bytes header"

def test_charts_handle_empty_datasets_safely():
    """Ensure chart generation doesn't crash on empty filters."""
    empty_chart = generate_package_distribution_chart(department="NonExistentBranch")
    assert isinstance(empty_chart, bytes)
    assert empty_chart.startswith(b"\x89PNG\r\n\x1a\n")
