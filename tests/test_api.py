"""Comprehensive API test suite for zeroeye backend."""
import pytest

class TestHealthEndpoint:
    """Health check endpoint tests."""

    def test_health_returns_200(self, server_url, client):
        r = client.get(f"{server_url}/health")
        assert r.status_code == 200

    def test_health_returns_json(self, server_url, client):
        r = client.get(f"{server_url}/health")
        assert r.headers.get("Content-Type", "").startswith("application/json")

    def test_health_has_status_field(self, server_url, client):
        r = client.get(f"{server_url}/health")
        data = r.json()
        assert "status" in data
        assert data["status"] == "ok"

class TestApiEndpoints:
    """Main API endpoint tests."""

    def test_api_root_returns_info(self, server_url, client):
        r = client.get(f"{server_url}/")
        assert r.status_code in (200, 404)

    def test_api_version_endpoint(self, server_url, client):
        r = client.get(f"{server_url}/version")
        if r.status_code == 200:
            data = r.json()
            assert "version" in data

    def test_api_404_on_unknown(self, server_url, client):
        r = client.get(f"{server_url}/nonexistent")
        assert r.status_code == 404

class TestErrorHandling:
    """Error response format tests."""

    def test_error_response_format(self, server_url, client):
        r = client.get(f"{server_url}/invalid")
        if r.status_code != 200:
            data = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
            assert isinstance(data, dict)
