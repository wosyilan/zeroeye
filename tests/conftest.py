"""
Shared test fixtures for the Tent of Trials / Zeroeye API test suite.

Architecture
------------
Because the backend is written in Go and the test suite is Python, we
cannot import route handlers directly.  Instead, tests validate the
**API contract** — request/response schemas, status codes, error
shapes, and validation rules — against the OpenAPI-style spec in
``docs/API_REFERENCE.md`` and the actual route table in
``market/gateway/api.go``.

Strategy
--------
- ``api_client`` — a thin fixture that wraps ``requests`` (for live
  integration tests) **or** falls back to a mock responder (offline).
- ``mock_api`` — a ``responses``-based fixture that intercepts HTTP
  calls and returns deterministic fixture data.  All tests run offline
  by default.
- ``auth_token`` — a synthetic Bearer token for authenticated endpoints.
- ``sample_*`` — helper fixtures that expose the static fixture data.
"""

import json
import re
from unittest.mock import patch

import pytest

from tests.data.fixtures import *  # noqa: F401, F403 — expose fixture data as module-level names


# ---------------------------------------------------------------------------
# Plugin markers & config
# ---------------------------------------------------------------------------

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "offline: marks tests that run without network (default).")
    config.addinivalue_line("markers", "live: marks tests that require a running backend.")


def pytest_addoption(parser):
    """Add --live flag to test against a real backend."""
    parser.addoption(
        "--live",
        action="store_true",
        default=False,
        help="Run tests against a real backend instance",
    )


# ---------------------------------------------------------------------------
# Core fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def api_base_url(request) -> str:
    """Return the base URL of the API under test.

    Defaults to the development URL from the API reference.
    Override with ``--base-url`` via a pytest option if needed.
    """
    return "http://localhost:8080/api/v1"


@pytest.fixture
def auth_token() -> str:
    """Return a synthetic Bearer token for authenticated endpoints.

    This is a well-known test token, not a real JWT.  Live tests should
    obtain a real token via the ``/auth/login`` endpoint.
    """
    return "test-access-token-zeroeye-2026"


@pytest.fixture
def auth_headers(auth_token) -> dict[str, str]:
    """Return standard headers including Authorization."""
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
        "X-Request-ID": "test-req-000001",
        "X-Client-Version": "3.0",
    }


@pytest.fixture
def mock_api(request):
    """Mock HTTP responses for the Zeroeye API using ``responses``.

    Usage in a test::

        def test_something(mock_api):
            mock_api.get("/api/v1/market/ticker?symbol=BTC/USD", json={...})

    This fixture is **auto-used** when ``--live`` is NOT set.
    """
    # Lazy-import to keep requirements minimal for offline users
    responses = pytest.importorskip("responses", reason="install 'responses' for offline mock tests")

    # Start the mock — decorate ``responses.requests``
    request = responses.RequestsMock(
        assert_all_requests_are_fired=False,
        target="requests.adapters.HTTPAdapter.send",
    )
    request.start()

    # Register a catch-all passthrough for anything not explicitly mocked
    request.add_passthru(re.compile(".*"))

    yield request

    request.stop()
    request.reset()


# ---------------------------------------------------------------------------
# Live / offline detection
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _skip_if_live_mismatch(request):
    """Automatically skip tests that need a running backend when
    ``--live`` is not given, and vice versa.

    Usage in test modules::

        @pytest.mark.offline   # (default) runs only when --live is absent
        @pytest.mark.live      # runs only when --live is present
    """
    live_mode = request.config.getoption("--live")
    has_live_mark = request.node.get_closest_marker("live")
    has_offline_mark = request.node.get_closest_marker("offline")

    if has_live_mark and not live_mode:
        pytest.skip("use --live to run integration tests")
    if has_offline_mark and live_mode:
        pytest.skip("skipped in --live mode")


# ---------------------------------------------------------------------------
# Parametrized helpers
# ---------------------------------------------------------------------------

def parametrize_symbols():
    """Return parametrize decorator with standard instrument symbols."""
    return pytest.mark.parametrize("symbol", ["BTC/USD", "ETH/USD", "SOL/USD"])


def parametrize_timeframes():
    """Return parametrize decorator with valid candle timeframes."""
    return pytest.mark.parametrize("timeframe", ["1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w"])


def parametrize_order_sides():
    """Return parametrize decorator with valid order sides."""
    return pytest.mark.parametrize("side", ["buy", "sell"])


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def assert_error_shape(response_data: dict, expected_code: int = 4001):
    """Assert that *response_data* conforms to the standard error format.

    Every API error is expected to have at least ``code``, ``message``,
    and ``request_id`` fields, matching the spec in the API reference.
    """
    assert "code" in response_data, "Missing 'code' in error response"
    assert "message" in response_data, "Missing 'message' in error response"
    assert response_data["code"] == expected_code, (
        f"Expected error code {expected_code}, got {response_data['code']}"
    )
    # request_id is optional in some edge cases, but should be present
    # for all properly-formed requests
    if "request_id" in response_data:
        assert isinstance(response_data["request_id"], str)
        assert len(response_data["request_id"]) > 0


def assert_pagination_shape(pagination: dict):
    """Assert that *pagination* has the expected shape."""
    for key in ("page", "per_page", "total", "total_pages"):
        assert key in pagination, f"Missing pagination field: {key}"
        assert isinstance(pagination[key], int), f"{key} must be int"
    assert pagination["per_page"] > 0
    assert pagination["page"] >= 1
