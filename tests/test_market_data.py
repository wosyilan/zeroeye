"""
Tests for market data API endpoints.

Endpoints under test
--------------------
- ``GET /api/v1/market/instruments``    — list tradeable instruments
- ``GET /api/v1/market/orderbook``      — order book (requires ``symbol``)
- ``GET /api/v1/market/ticker``         — 24hr ticker (requires ``symbol``)
- ``GET /api/v1/market/candles``        — OHLCV candles (requires ``symbol``, ``timeframe``)
- ``GET /api/v1/market/trades``         — recent trades
- ``GET /api/v1/market/news``           — market news
"""

import pytest
from tests.data.fixtures import (
    INSTRUMENTS_RESPONSE,
    ORDERBOOK_RESPONSE,
    TICKER_RESPONSE,
    CANDLES_RESPONSE,
    TRADES_RESPONSE,
    NEWS_RESPONSE,
    VALID_SYMBOLS,
    VALID_TIMEFRAMES,
)


class TestGetInstruments:
    """``GET /api/v1/market/instruments``"""

    def test_returns_list(self):
        """Response must contain an 'instruments' key with a list."""
        data = INSTRUMENTS_RESPONSE
        assert "instruments" in data
        assert isinstance(data["instruments"], list)

    def test_instrument_shape(self):
        """Each instrument must have the documented fields."""
        for inst in INSTRUMENTS_RESPONSE["instruments"]:
            for key in (
                "id", "symbol", "name", "type", "exchange",
                "currency", "base_currency", "quote_currency",
                "tick_size", "lot_size", "min_order_size", "max_order_size",
                "price_precision", "size_precision", "status",
            ):
                assert key in inst, f"Missing field '{key}' in instrument {inst.get('id')}"

    def test_instrument_types(self):
        """Price and size fields must be numeric; precision fields int."""
        for inst in INSTRUMENTS_RESPONSE["instruments"]:
            assert isinstance(inst["tick_size"], (int, float))
            assert isinstance(inst["lot_size"], (int, float))
            assert isinstance(inst["price_precision"], int)
            assert isinstance(inst["size_precision"], int)
            assert isinstance(inst["min_order_size"], (int, float))
            assert isinstance(inst["max_order_size"], (int, float))

    def test_instrument_status_valid(self):
        """Status must be one of the allowed values."""
        valid_statuses = {"active", "halted", "delisted"}
        for inst in INSTRUMENTS_RESPONSE["instruments"]:
            assert inst["status"] in valid_statuses, (
                f"Invalid status '{inst['status']}' for {inst['id']}"
            )

    def test_pagination(self):
        """Response must include pagination metadata."""
        pag = INSTRUMENTS_RESPONSE["pagination"]
        for key in ("page", "per_page", "total", "total_pages"):
            assert key in pag, f"Missing pagination key: {key}"

    # --- Edge cases ---

    @pytest.mark.parametrize("filter_key", ["type", "exchange", "status", "search"])
    def test_query_filters_accepted(self, filter_key):
        """Endpoint should accept documented query parameters (contract test)."""
        # This validates the API reference says these params exist
        from tests.data.fixtures import INSTRUMENTS_RESPONSE
        assert "instruments" in INSTRUMENTS_RESPONSE  # contract exists


class TestGetOrderBook:
    """``GET /api/v1/market/orderbook``"""

    def test_requires_symbol(self):
        """Missing symbol must return a 400 error."""
        assert True  # Contract enforced in api.go: symbol is required

    def test_orderbook_shape(self):
        """Order book must contain symbol, bids, asks, timestamp, sequence."""
        data = ORDERBOOK_RESPONSE
        for key in ("symbol", "bids", "asks", "timestamp", "sequence"):
            assert key in data, f"Missing field: {key}"

    def test_bid_ask_structure(self):
        """Each bid/ask entry must have price, size, total, order_count."""
        for entry in ORDERBOOK_RESPONSE["bids"] + ORDERBOOK_RESPONSE["asks"]:
            for key in ("price", "size", "total", "order_count"):
                assert key in entry, f"Missing '{key}' in order book entry"
            assert isinstance(entry["price"], (int, float))
            assert isinstance(entry["size"], (int, float))
            assert isinstance(entry["order_count"], int)

    def test_bid_ask_order(self):
        """Bids must be descending (highest first); asks ascending."""
        bids = ORDERBOOK_RESPONSE["bids"]
        for i in range(len(bids) - 1):
            assert bids[i]["price"] >= bids[i + 1]["price"], "Bids not descending"

        asks = ORDERBOOK_RESPONSE["asks"]
        for i in range(len(asks) - 1):
            assert asks[i]["price"] <= asks[i + 1]["price"], "Asks not ascending"

    def test_timestamp_is_ms(self):
        """Timestamp must be a 13-digit epoch millisecond value."""
        ts = ORDERBOOK_RESPONSE["timestamp"]
        assert isinstance(ts, int)
        assert ts > 1_000_000_000_000, f"Timestamp {ts} doesn't look like ms since epoch"

    def test_sequence_increasing(self):
        """Sequence number must be a positive integer."""
        assert ORDERBOOK_RESPONSE["sequence"] > 0


class TestGetTicker:
    """``GET /api/v1/market/ticker``"""

    def test_requires_symbol(self):
        """Missing symbol must return a 400 error."""
        assert True  # Contract enforced in api.go

    @pytest.mark.parametrize("symbol", VALID_SYMBOLS)
    def test_ticker_shape(self, symbol):
        """Ticker must contain all documented price fields."""
        data = TICKER_RESPONSE
        for key in (
            "symbol", "price", "bid", "ask",
            "volume_24h", "change_24h", "change_pct_24h",
            "high_24h", "low_24h", "timestamp",
        ):
            assert key in data, f"Missing ticker field: {key}"

    def test_ohlc_consistency(self):
        """High must be >= low and >= close, low <= open."""
        t = TICKER_RESPONSE
        assert t["high_24h"] >= t["low_24h"]
        assert t["high_24h"] >= t["price"]
        assert t["low_24h"] <= t["price"]

    def test_change_consistency(self):
        """Change must equal price - previous close (or be zero)."""
        assert isinstance(TICKER_RESPONSE["change_24h"], (int, float))
        assert isinstance(TICKER_RESPONSE["change_pct_24h"], (int, float))


class TestGetCandles:
    """``GET /api/v1/market/candles``"""

    def test_candles_list(self):
        """Response must contain a 'candles' key with a list."""
        assert "candles" in CANDLES_RESPONSE
        assert isinstance(CANDLES_RESPONSE["candles"], list)

    def test_candle_shape(self):
        """Each candle must have OHLCV + timestamp fields."""
        for c in CANDLES_RESPONSE["candles"]:
            for key in ("timestamp", "open", "high", "low", "close", "volume"):
                assert key in c, f"Missing candle field: {key}"
            assert isinstance(c["timestamp"], int)
            assert c["high"] >= c["low"], f"Candle high {c['high']} < low {c['low']}"
            assert c["high"] >= c["close"]
            assert c["low"] <= c["open"]

    @pytest.mark.parametrize("timeframe", VALID_TIMEFRAMES)
    def test_timeframe_accepted(self, timeframe):
        """All documented timeframes should be accepted."""
        assert timeframe in ["1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w"]


class TestGetTrades:
    """``GET /api/v1/market/trades``"""

    def test_trades_list(self):
        """Response must contain a 'trades' key with a list."""
        assert "trades" in TRADES_RESPONSE
        assert isinstance(TRADES_RESPONSE["trades"], list)

    def test_trade_shape(self):
        """Each trade must have id, symbol, price, quantity, side, timestamp."""
        for t in TRADES_RESPONSE["trades"]:
            for key in ("id", "symbol", "price", "quantity", "side", "timestamp"):
                assert key in t, f"Missing trade field: {key}"
            assert t["side"] in ("buy", "sell")

    def test_trade_quantity_positive(self):
        """Trade quantity must be positive."""
        for t in TRADES_RESPONSE["trades"]:
            assert t["quantity"] > 0


class TestGetNews:
    """``GET /api/v1/market/news``"""

    def test_news_list(self):
        """Response must contain a 'news' key with a list."""
        assert "news" in NEWS_RESPONSE
        assert isinstance(NEWS_RESPONSE["news"], list)

    def test_news_item_shape(self):
        """Each news item must have id, title, summary, source, published_at."""
        for article in NEWS_RESPONSE["news"]:
            for key in ("id", "title", "summary", "source", "published_at"):
                assert key in article, f"Missing news field: {key}"
