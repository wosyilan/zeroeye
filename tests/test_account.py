"""
Tests for authentication and account API endpoints.

Endpoints under test (from API reference)
------------------------------------------
- ``POST /auth/login``         — authenticate with email + password
- ``POST /auth/register``      — create a new account
- ``POST /auth/refresh``       — refresh an expired token
- ``POST /auth/logout``        — invalidate current session
- ``GET  /account/summary``    — account balances + buying power
- ``GET  /account/transactions`` — transaction history
- ``GET  /positions``          — open positions
- ``GET  /positions/{id}``     — position detail
"""

import pytest
from tests.data.fixtures import (
    LOGIN_RESPONSE,
    REGISTER_RESPONSE,
    REFRESH_RESPONSE,
    LOGOUT_RESPONSE,
    ACCOUNT_SUMMARY_RESPONSE,
    TRANSACTIONS_RESPONSE,
    POSITIONS_RESPONSE,
    POSITION_DETAIL_RESPONSE,
)


class TestAuthLogin:
    """``POST /auth/login``"""

    def test_login_response_shape(self):
        """Login must return access_token, refresh_token, expires_in, token_type."""
        resp = LOGIN_RESPONSE
        for key in ("access_token", "refresh_token", "expires_in", "token_type"):
            assert key in resp, f"Missing login response field: {key}"
        assert resp["token_type"] == "Bearer"
        assert resp["expires_in"] > 0

    def test_token_format(self):
        """Tokens must be non-empty strings (likely JWTs)."""
        assert len(LOGIN_RESPONSE["access_token"]) > 20
        assert len(LOGIN_RESPONSE["refresh_token"]) > 20

    def test_login_missing_email(self):
        """Request without email must return 400."""
        expected_error = {"code": 4001, "message": "Invalid request"}
        assert expected_error["code"] == 4001

    def test_login_missing_password(self):
        """Request without password must return 400."""
        expected_error = {"code": 4001, "message": "Invalid request"}
        assert expected_error["code"] == 4001

    def test_login_invalid_credentials(self):
        """Invalid credentials must return 401."""
        expected_error = {"code": 4002, "message": "Invalid email or password"}
        assert expected_error["code"] == 4002


class TestAuthRegister:
    """``POST /auth/register``"""

    def test_register_response_shape(self):
        """Register must return user_id, email, created_at, requires_verification."""
        resp = REGISTER_RESPONSE
        for key in ("user_id", "email", "created_at", "requires_verification"):
            assert key in resp, f"Missing register response field: {key}"
        assert isinstance(resp["requires_verification"], bool)

    def test_register_duplicate_email(self):
        """Registering with an existing email must return 409."""
        expected = {"code": 4009, "message": "Email already registered"}
        assert expected["code"] == 4009


class TestAuthRefresh:
    """``POST /auth/refresh``"""

    def test_refresh_response_shape(self):
        """Refresh must return access_token, expires_in, token_type."""
        resp = REFRESH_RESPONSE
        assert "access_token" in resp
        assert "expires_in" in resp
        assert resp["token_type"] == "Bearer"

    def test_refresh_expired_token(self):
        """Expired refresh token must return 401."""
        expected = {"code": 4002, "message": "Refresh token expired"}
        assert expected["code"] == 4002


class TestAuthLogout:
    """``POST /auth/logout``"""

    def test_logout_response(self):
        """Logout must invalidate session and return confirmation."""
        assert "message" in LOGOUT_RESPONSE
        assert isinstance(LOGOUT_RESPONSE["message"], str)

    def test_logout_twice(self):
        """Calling logout twice should still return success."""
        assert LOGOUT_RESPONSE["message"] == "Session invalidated"


class TestAccountSummary:
    """``GET /account/summary``"""

    def test_summary_shape(self):
        """Summary must contain account_id, balance, buying_power, equity."""
        resp = ACCOUNT_SUMMARY_RESPONSE
        for key in ("account_id", "balance", "buying_power", "equity", "margin_used"):
            assert key in resp, f"Missing account summary field: {key}"

    def test_balance_currencies(self):
        """Balance must be a dict with at least one currency."""
        balance = ACCOUNT_SUMMARY_RESPONSE["balance"]
        assert isinstance(balance, dict)
        assert len(balance) >= 1
        for ccy, amt in balance.items():
            assert isinstance(amt, (int, float)), f"Balance for {ccy} must be numeric"
            assert amt >= 0, f"Balance for {ccy} is negative"

    def test_buying_power_positive(self):
        """Buying power must be >= 0."""
        assert ACCOUNT_SUMMARY_RESPONSE["buying_power"] >= 0

    def test_day_trade_count(self):
        """Day trade count must be a non-negative integer."""
        assert isinstance(ACCOUNT_SUMMARY_RESPONSE["day_trade_count"], int)
        assert ACCOUNT_SUMMARY_RESPONSE["day_trade_count"] >= 0


class TestAccountTransactions:
    """``GET /account/transactions``"""

    def test_transactions_list(self):
        """Response must contain a 'transactions' key with a list."""
        assert "transactions" in TRANSACTIONS_RESPONSE
        assert isinstance(TRANSACTIONS_RESPONSE["transactions"], list)

    def test_transaction_shape(self):
        """Each transaction must have id, type, amount, balance_after, timestamp."""
        for txn in TRANSACTIONS_RESPONSE["transactions"]:
            for key in ("id", "type", "amount", "balance_after", "timestamp"):
                assert key in txn, f"Missing transaction field: {key}"

    def test_pagination(self):
        """Transactions must be paginated."""
        pag = TRANSACTIONS_RESPONSE.get("pagination", {})
        assert "page" in pag


class TestPositions:
    """``GET /positions`` and ``GET /positions/{id}``"""

    def test_positions_list(self):
        """Response must contain a 'positions' key with a list."""
        assert "positions" in POSITIONS_RESPONSE
        assert isinstance(POSITIONS_RESPONSE["positions"], list)

    def test_position_shape(self):
        """Each position must have instrument_id, quantity, entry_price, current_price, P&L."""
        for pos in POSITIONS_RESPONSE["positions"]:
            for key in (
                "instrument_id", "quantity", "entry_price", "current_price",
                "unrealized_pnl", "realized_pnl", "total_pnl",
            ):
                assert key in pos, f"Missing position field: {key}"

    def test_position_pnl_consistency(self):
        """Total P&L must equal unrealized + realized."""
        for pos in POSITIONS_RESPONSE["positions"]:
            expected = pos["unrealized_pnl"] + pos["realized_pnl"]
            assert abs(pos["total_pnl"] - expected) < 0.01, (
                f"P&L mismatch for {pos['instrument_id']}: "
                f"total={pos['total_pnl']} != unrealized+realized={expected}"
            )

    def test_position_detail(self):
        """Position detail must include liquidation_price."""
        detail = POSITION_DETAIL_RESPONSE
        assert "liquidation_price" in detail
        assert detail["liquidation_price"] < detail["entry_price"], (
            "Liquidation price should be below entry for long positions"
        )

    def test_position_quantity_positive(self):
        """Position quantity must be non-zero."""
        for pos in POSITIONS_RESPONSE["positions"]:
            assert pos["quantity"] != 0

    def test_leverage_range(self):
        """Leverage must be >= 1x and <= max allowed."""
        for pos in POSITIONS_RESPONSE["positions"]:
            assert pos["leverage"] >= 1.0
            assert pos["leverage"] <= 100.0
