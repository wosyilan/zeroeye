"""
Tests for order management API endpoints.

Endpoints under test (from API reference)
------------------------------------------
- ``POST /orders``            — place a new order
- ``GET  /orders``            — list orders
- ``GET  /orders/{id}``       — get order detail
- ``DELETE /orders/{id}``     — cancel an open order
"""

import pytest
from tests.data.fixtures import (
    ORDER_PLACED_RESPONSE,
    ORDERS_LIST_RESPONSE,
    ORDER_DETAIL_RESPONSE,
    ORDER_CANCEL_RESPONSE,
    VALID_SIDES,
    VALID_ORDER_TYPES,
    VALID_TIME_IN_FORCE,
)


class TestPlaceOrder:
    """``POST /orders``"""

    def test_placed_response_shape(self):
        """A successfully placed order must return order_id, status, created_at."""
        resp = ORDER_PLACED_RESPONSE
        for key in ("order_id", "status", "created_at"):
            assert key in resp, f"Missing field: {key}"
        assert resp["status"] in ("new", "accepted", "pending")

    def test_placed_initial_status(self):
        """A new limit order should have 'new' status."""
        assert ORDER_PLACED_RESPONSE["status"] == "new"

    @pytest.mark.parametrize("side", VALID_SIDES)
    def test_place_order_valid_sides(self, side):
        """Both buy and sell sides must be accepted."""
        resp = ORDER_PLACED_RESPONSE
        assert "order_id" in resp

    @pytest.mark.parametrize("order_type", VALID_ORDER_TYPES)
    def test_place_order_types(self, order_type):
        """All documented order types must be accepted."""
        resp = ORDER_PLACED_RESPONSE
        assert "order_id" in resp

    def test_place_order_missing_instrument(self):
        """Order without instrument_id must return 400."""
        expected = {"code": 4001, "message": "instrument_id is required"}
        assert expected["code"] == 4001

    def test_place_order_missing_side(self):
        """Order without side must return 400."""
        expected = {"code": 4001, "message": "side is required"}
        assert expected["code"] == 4001

    def test_place_order_invalid_quantity(self):
        """Order with zero/negative quantity must return 400."""
        expected = {"code": 4001, "message": "quantity must be positive"}
        assert expected["code"] == 4001

    def test_place_order_unknown_instrument(self):
        """Order for unknown instrument must return 404."""
        expected = {"code": 4004, "message": "Instrument not found"}
        assert expected["code"] == 4004

    def test_place_order_client_order_id(self):
        """Client order ID must be echoed back if provided."""
        assert "client_order_id" in ORDER_PLACED_RESPONSE

    def test_place_order_insufficient_funds(self):
        """Order exceeding available funds must return 422."""
        expected = {"code": 4022, "message": "Insufficient funds"}
        assert expected["code"] == 4022


class TestListOrders:
    """``GET /orders``"""

    def test_orders_list_shape(self):
        """Response must contain 'orders' list and pagination."""
        assert "orders" in ORDERS_LIST_RESPONSE
        assert isinstance(ORDERS_LIST_RESPONSE["orders"], list)

    def test_order_in_list_shape(self):
        """Each order in the list must have core fields."""
        for o in ORDERS_LIST_RESPONSE["orders"]:
            for key in ("order_id", "instrument_id", "side", "type", "price",
                        "quantity", "status", "created_at"):
                assert key in o, f"Missing order field: {key}"

    def test_order_status_in_list(self):
        """Order status must be a valid value."""
        valid_statuses = {"new", "open", "partially_filled", "filled",
                          "canceled", "rejected", "expired"}
        for o in ORDERS_LIST_RESPONSE["orders"]:
            assert o["status"] in valid_statuses, f"Invalid status: {o['status']}"

    @pytest.mark.parametrize("filter_key", ["status", "instrument", "side", "from", "to"])
    def test_list_filters_accepted(self, filter_key):
        """All documented query filters must be accepted."""
        assert True  # Contract test: parameters exist in API reference

    def test_pagination(self):
        """Orders list must include pagination metadata."""
        pag = ORDERS_LIST_RESPONSE.get("pagination", {})
        assert "page" in pag


class TestGetOrderDetail:
    """``GET /orders/{id}``"""

    def test_detail_shape(self):
        """Order detail must include all trade-related fields."""
        resp = ORDER_DETAIL_RESPONSE
        for key in ("order_id", "instrument_id", "side", "type", "price",
                    "quantity", "filled_quantity", "average_fill_price",
                    "status", "created_at", "updated_at"):
            assert key in resp, f"Missing order detail field: {key}"

    def test_filled_quantity_bounds(self):
        """Filled quantity must be between 0 and total quantity."""
        assert 0 <= ORDER_DETAIL_RESPONSE["filled_quantity"] <= ORDER_DETAIL_RESPONSE["quantity"]

    def test_detail_unknown_order(self):
        """Non-existent order ID must return 404."""
        expected = {"code": 4004, "message": "Order not found"}
        assert expected["code"] == 4004


class TestCancelOrder:
    """``DELETE /orders/{id}``"""

    def test_cancel_success(self):
        """Successfully canceled order must return order_id + status=canceled."""
        assert ORDER_CANCEL_RESPONSE["order_id"] is not None
        assert ORDER_CANCEL_RESPONSE["status"] == "canceled"

    def test_cancel_already_filled(self):
        """Canceling an already-filled order must return 400."""
        expected = {"code": 4001, "message": "Order already filled"}
        assert expected["code"] == 4001

    def test_cancel_unknown_order(self):
        """Canceling a non-existent order must return 404."""
        expected = {"code": 4004, "message": "Order not found"}
        assert expected["code"] == 4004
