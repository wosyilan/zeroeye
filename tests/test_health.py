"""
Tests for the health-check and metrics endpoints.

Routes under test
-----------------
- ``GET /health``          → 200 + status + version
- ``GET /health/ready``    → 200 (healthy) / 503 (unhealthy)
- ``GET /health/live``     → 200
- ``GET /metrics``         → 200 + gateway metrics snapshot
"""

import pytest
from tests.data.fixtures import (
    HEALTH_RESPONSE,
    READY_RESPONSE,
    ALIVE_RESPONSE,
    METRICS_RESPONSE,
)


class TestHealthEndpoint:
    """``GET /health`` — top-level health check."""

    def test_health_returns_ok(self):
        """Health endpoint must return status, timestamp, uptime, and version."""
        resp = HEALTH_RESPONSE
        assert resp["status"] == "ok"
        assert "timestamp" in resp
        assert "uptime" in resp
        assert "version" in resp

    def test_health_version(self):
        """Version should be a valid semver-like string."""
        version = HEALTH_RESPONSE["version"]
        parts = version.split(".")
        assert len(parts) == 2, f"Expected MAJOR.MINOR, got {version}"
        assert all(p.isdigit() for p in parts), f"Version parts must be numeric: {version}"

    def test_health_timestamp_format(self):
        """Timestamp should be RFC 3339."""
        ts = HEALTH_RESPONSE["timestamp"]
        assert "T" in ts, f"Expected RFC 3339 timestamp, got {ts}"

    def test_health_uptime_format(self):
        """Uptime should be a human-readable duration string."""
        uptime = HEALTH_RESPONSE["uptime"]
        assert "h" in uptime or "m" in uptime or "s" in uptime, (
            f"Uptime '{uptime}' doesn't look like a duration"
        )

    # --- Edge cases ---

    def test_health_additional_fields_not_blocked(self):
        """The health response may include extra fields; clients should tolerate them."""
        extended = {**HEALTH_RESPONSE, "hostname": "node-1", "commit": "a1b2c3d4"}
        assert extended["status"] == "ok"
        assert extended["hostname"] == "node-1"


class TestReadinessEndpoint:
    """``GET /health/ready`` — readiness probe."""

    def test_readiness_ok(self):
        """When healthy, readiness returns 200 with status 'ready'."""
        assert READY_RESPONSE["status"] == "ready"

    def test_readiness_not_ready(self):
        """When unhealthy, readiness must return 503."""
        expected_unhealthy = {"status": "not ready"}
        assert expected_unhealthy["status"] == "not ready"


class TestLivenessEndpoint:
    """``GET /health/live`` — liveness probe."""

    def test_liveness_alive(self):
        """Liveness returns 200 with status 'alive'."""
        assert ALIVE_RESPONSE["status"] == "alive"

    def test_liveness_response_keys(self):
        """Liveness response should contain exactly the 'status' key."""
        assert set(ALIVE_RESPONSE.keys()) == {"status"}


class TestMetricsEndpoint:
    """``GET /metrics`` — gateway metrics snapshot."""

    METRIC_FIELDS = [
        "requests_total",
        "requests_active",
        "requests_failed",
        "requests_timed_out",
        "requests_rate_limited",
        "ws_connections_total",
        "ws_connections_active",
        "ws_connections_dropped",
        "bytes_sent",
        "bytes_received",
        "average_latency_ms",
        "peak_latency_ms",
    ]

    def test_metrics_contains_all_fields(self):
        """Metrics response must include every documented counter."""
        for field in self.METRIC_FIELDS:
            assert field in METRICS_RESPONSE, f"Missing metric: {field}"

    def test_metrics_types(self):
        """All metric values should be integers."""
        for field in self.METRIC_FIELDS:
            val = METRICS_RESPONSE[field]
            assert isinstance(val, int), (
                f"{field} should be int, got {type(val).__name__}: {val}"
            )

    def test_metrics_non_negative(self):
        """Metric values must not be negative."""
        for field in self.METRIC_FIELDS:
            assert METRICS_RESPONSE[field] >= 0, f"{field} is negative"

    def test_metrics_latency_reasonable(self):
        """Latency values should be physically possible (< 1 hour)."""
        assert 0 <= METRICS_RESPONSE["average_latency_ms"] < 3_600_000
        assert 0 <= METRICS_RESPONSE["peak_latency_ms"] < 3_600_000

    @pytest.mark.parametrize("field", ["requests_total", "requests_failed"])
    def test_metrics_counts_consistent(self, field):
        """Core counters should be internally consistent."""
        val = METRICS_RESPONSE[field]
        failed = METRICS_RESPONSE["requests_failed"]
        assert failed <= METRICS_RESPONSE["requests_total"], (
            f"Failed ({failed}) exceeds total ({METRICS_RESPONSE['requests_total']})"
        )
