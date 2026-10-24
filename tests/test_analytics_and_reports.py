"""
Unit & Integration Tests for Analytics Modules and Printable Report Generations.
"""

import pytest


def test_analytics_sub_views(officer_client):
    """Verify deep analytical breakdown views render properly."""
    sub_views = [
        "/analytics/",
        "/analytics/departments",
        "/analytics/packages",
        "/analytics/skills",
        "/analytics/trends",
    ]
    for url in sub_views:
        resp = officer_client.get(url)
        assert resp.status_code == 200, f"Failed on {url}"


def test_all_reports_types(officer_client):
    """Verify all report views render properly for placement officers."""
    report_types = ["summary", "department", "companies", "skills", "packages", "students"]
    for rtype in report_types:
        resp = officer_client.get(f"/reports/?type={rtype}")
        assert resp.status_code == 200, f"Report type {rtype} failed"


def test_api_statistics_and_charts(officer_client):
    """Verify JSON statistics and streaming chart endpoints."""
    stats_resp = officer_client.get("/api/stats")
    assert stats_resp.status_code == 200
    assert stats_resp.get_json()["success"] is True

    chart_data_resp = officer_client.get("/api/chart-data?department=All&graduation_year=All")
    assert chart_data_resp.status_code == 200
    cd = chart_data_resp.get_json()
    assert cd["success"] is True
    assert "dept_rates" in cd
    assert "skills" in cd
    assert "companies" in cd
    assert "trends" in cd

    chart_endpoints = [
        "/api/charts/dept-rate",
        "/api/charts/placed-vs-eligible",
        "/api/charts/package-distribution",
        "/api/charts/top-skills",
        "/api/charts/company-hires",
        "/api/charts/yearly-trends",
    ]
    for curl in chart_endpoints:
        cresp = officer_client.get(curl)
        assert cresp.status_code == 200, f"Chart {curl} failed"
        assert cresp.mimetype == "image/png"


def test_reports_csv_exports(officer_client):
    """Verify CSV export functionality for all report modalities."""
    modalities = ["summary", "department", "companies", "skills", "packages", "students"]
    for m in modalities:
        resp = officer_client.get(f"/reports/export-csv?type={m}")
        assert resp.status_code == 200, f"Failed export for modality {m}"
        assert resp.mimetype == "text/csv"
        assert len(resp.data) > 0
