"""Tests for OpenAPI Specification and Swagger UI endpoints."""


def test_swagger_ui_endpoint(officer_client):
    """Test that the Swagger UI documentation page loads correctly."""
    response = officer_client.get("/api/docs")
    assert response.status_code == 200
    assert b"SwaggerUIBundle" in response.data or b"swagger-ui" in response.data
    assert b"API Documentation | Student Placement Analytics" in response.data


def test_openapi_yaml_endpoint(officer_client):
    """Test that the raw OpenAPI 3.0.3 YAML is served with proper content type."""
    response = officer_client.get("/api/openapi.yaml")
    assert response.status_code == 200
    assert (
        b"text/yaml" in response.headers["Content-Type"].encode()
        or b"text/plain" in response.headers["Content-Type"].encode()
    )
    assert b"openapi: 3.0.3" in response.data


def test_chart_data_endpoint(officer_client):
    """Test the dynamic Chart.js JSON dataset endpoint."""
    response = officer_client.get("/api/chart-data?department=All&graduation_year=All")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["success"] is True
    assert "dept_rates" in json_data
    assert "companies" in json_data
    assert "package_stats" in json_data
    assert "skills" in json_data
    assert "trends" in json_data
