"""
Static test data matching the API Reference schema.

These fixtures provide realistic sample data for every documented
endpoint so tests don't depend on a running backend or real market data.
"""

HEALTH_RESPONSE = {
    "status": "ok",
    "timestamp": "2026-01-15T10:30:00Z",
    "uptime": "72h15m30s",
    "version": "3.0",
}

READY_RESPONSE = {"status": "ready"}
ALIVE_RESPONSE = {"status": "alive"}

METRICS_RESPONSE = {
    "requests_total": 15234,
    "requests_active": 3,
    "requests_failed": 12,
    "requests_timed_out": 2,
    "requests_rate_limited": 5,
    "ws_connections_total": 450,
    "ws_connections_active": 28,
    "ws_connections_dropped": 7,
    "bytes_sent": 104857600,
    "bytes_received": 52428800,
    "average_latency_ms": 45,
    "peak_latency_ms": 320,
}

INSTRUMENTS_RESPONSE = {
    "instruments": [
        {
            "id": "btc-usd",
            "symbol": "BTC/USD",
            "name": "Bitcoin / US Dollar",
            "type": "crypto",
            "exchange": "internal",
            "currency": "USD",
            "base_currency": "BTC",
            "quote_currency": "USD",
            "tick_size": 0.01,
            "lot_size": 0.0001,
            "min_order_size": 0.001,
            "max_order_size": 1000,
            "price_precision": 2,
            "size_precision": 4,
            "status": "active",
        },
        {
            "id": "eth-usd",
            "symbol": "ETH/USD",
            "name": "Ethereum / US Dollar",
            "type": "crypto",
            "exchange": "internal",
            "currency": "USD",
            "base_currency": "ETH",
            "quote_currency": "USD",
            "tick_size": 0.01,
            "lot_size": 0.001,
            "min_order_size": 0.01,
            "max_order_size": 5000,
            "price_precision": 2,
            "size_precision": 3,
            "status": "active",
        },
    ],
    "pagination": {"page": 1, "per_page": 50, "total": 2, "total_pages": 1},
}

ORDERBOOK_RESPONSE = {
    "symbol": "BTC/USD",
    "bids": [
        {"price": 50000.00, "size": 1.5, "total": 1.5, "order_count": 3},
        {"price": 49990.00, "size": 2.0, "total": 3.5, "order_count": 4},
    ],
    "asks": [
        {"price": 50010.00, "size": 1.2, "total": 1.2, "order_count": 2},
        {"price": 50020.00, "size": 0.8, "total": 2.0, "order_count": 1},
    ],
    "timestamp": 1704070800000,
    "sequence": 12345678,
}

TICKER_RESPONSE = {
    "symbol": "BTC/USD",
    "price": 50000.00,
    "bid": 49999.00,
    "ask": 50001.00,
    "volume_24h": 12500.5,
    "change_24h": 250.00,
    "change_pct_24h": 0.50,
    "high_24h": 50200.00,
    "low_24h": 49700.00,
    "timestamp": 1704070800000,
}

CANDLES_RESPONSE = {
    "candles": [
        {
            "timestamp": 1704070800000,
            "open": 50000.00,
            "high": 50100.00,
            "low": 49950.00,
            "close": 50050.00,
            "volume": 125.5,
        },
        {
            "timestamp": 1704070860000,
            "open": 50050.00,
            "high": 50150.00,
            "low": 50000.00,
            "close": 50100.00,
            "volume": 98.2,
        },
    ]
}

TRADES_RESPONSE = {
    "trades": [
        {
            "id": "trade_001",
            "symbol": "BTC/USD",
            "price": 50000.00,
            "quantity": 0.5,
            "side": "buy",
            "timestamp": 1704070800000,
        },
        {
            "id": "trade_002",
            "symbol": "BTC/USD",
            "price": 50010.00,
            "quantity": 0.3,
            "side": "sell",
            "timestamp": 1704070860000,
        },
    ]
}

NEWS_RESPONSE = {
    "news": [
        {
            "id": "news_001",
            "title": "Bitcoin reaches new all-time high",
            "summary": "BTC surpassed previous record amid institutional buying.",
            "source": "CryptoNews",
            "symbol": "BTC/USD",
            "published_at": 1704070800000,
            "url": "https://example.com/news/001",
        }
    ]
}

LOGIN_RESPONSE = {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "expires_in": 3600,
    "token_type": "Bearer",
}

REGISTER_RESPONSE = {
    "user_id": "usr_abc123",
    "email": "user@example.com",
    "created_at": "2026-01-15T10:30:00Z",
    "requires_verification": True,
}

REFRESH_RESPONSE = {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "expires_in": 3600,
    "token_type": "Bearer",
}

LOGOUT_RESPONSE = {"message": "Session invalidated"}

ORDER_PLACED_RESPONSE = {
    "order_id": "ord_abc123",
    "status": "new",
    "created_at": "2026-01-15T10:30:00Z",
    "client_order_id": "my-order-123",
}

ORDERS_LIST_RESPONSE = {
    "orders": [
        {
            "order_id": "ord_abc123",
            "instrument_id": "btc-usd",
            "side": "buy",
            "type": "limit",
            "price": 50000.00,
            "quantity": 0.1,
            "filled_quantity": 0.0,
            "status": "new",
            "created_at": "2026-01-15T10:30:00Z",
            "client_order_id": "my-order-123",
        }
    ],
    "pagination": {"page": 1, "per_page": 50, "total": 1, "total_pages": 1},
}

ORDER_DETAIL_RESPONSE = {
    "order_id": "ord_abc123",
    "instrument_id": "btc-usd",
    "side": "buy",
    "type": "limit",
    "price": 50000.00,
    "quantity": 0.1,
    "filled_quantity": 0.05,
    "average_fill_price": 50000.00,
    "status": "partially_filled",
    "created_at": "2026-01-15T10:30:00Z",
    "updated_at": "2026-01-15T10:31:00Z",
    "client_order_id": "my-order-123",
}

ORDER_CANCEL_RESPONSE = {"order_id": "ord_abc123", "status": "canceled"}

ACCOUNT_SUMMARY_RESPONSE = {
    "account_id": "acc_abc123",
    "balance": {
        "USD": 50000.00,
        "BTC": 1.5,
        "ETH": 10.0,
    },
    "buying_power": 75000.00,
    "equity": 150000.00,
    "margin_used": 0.00,
    "day_trade_count": 3,
}

TRANSACTIONS_RESPONSE = {
    "transactions": [
        {
            "id": "txn_001",
            "type": "trade",
            "instrument": "BTC/USD",
            "amount": -50000.00,
            "balance_after": 50000.00,
            "timestamp": 1704070800000,
            "description": "Market buy 1 BTC @ 50000.00",
        }
    ],
    "pagination": {"page": 1, "per_page": 50, "total": 1, "total_pages": 1},
}

POSITIONS_RESPONSE = {
    "positions": [
        {
            "instrument_id": "btc-usd",
            "quantity": 1.5,
            "entry_price": 48000.00,
            "current_price": 50000.00,
            "unrealized_pnl": 3000.00,
            "realized_pnl": 500.00,
            "total_pnl": 3500.00,
            "margin_used": 24000.00,
            "leverage": 1.0,
        }
    ]
}

POSITION_DETAIL_RESPONSE = {
    "instrument_id": "btc-usd",
    "quantity": 1.5,
    "entry_price": 48000.00,
    "current_price": 50000.00,
    "unrealized_pnl": 3000.00,
    "realized_pnl": 500.00,
    "total_pnl": 3500.00,
    "margin_used": 24000.00,
    "leverage": 1.0,
    "liquidation_price": 40000.00,
}

# Standard error response template
ERROR_TEMPLATE = {
    "code": 4001,
    "message": "Invalid request parameters",
    "request_id": "req_abc123",
    "details": {"field": "symbol", "reason": "Unknown instrument symbol"},
}

VALID_SYMBOLS = ["BTC/USD", "ETH/USD", "SOL/USD"]
VALID_TIMEFRAMES = ["1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w"]
VALID_SIDES = ["buy", "sell"]
VALID_ORDER_TYPES = ["market", "limit", "stop", "stop_limit"]
VALID_TIME_IN_FORCE = ["gtc", "ioc", "fok", "day"]
