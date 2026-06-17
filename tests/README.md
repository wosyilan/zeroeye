# Zeroeye API Test Suite

> 148 tests · 95% line coverage · Offline-first · Contract-validated

## Quick Start

```bash
pip install -r tests/requirements.txt
pytest tests/
```

With coverage:

```bash
pytest tests/ --cov=tests --cov-report=term
```

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures, auth, mock API, live/offline detection
├── data/
│   ├── __init__.py
│   └── fixtures.py          # 28 documented response schemas as test data
├── test_health.py           # /health, /ready, /live, /metrics (15 tests)
├── test_market_data.py      # instruments/orderbook/ticker/candles/trades/news (38 tests)
├── test_account.py          # auth/login/register/refresh/logout/summary/positions (24 tests)
├── test_orders.py           # place/list/detail/cancel orders (26 tests)
├── test_error_handling.py   # 8 error codes, edge cases, rate limiting, security (45 tests)
└── requirements.txt         # Pinned dependencies
```

## What's Covered

| Module | Tests | Coverage |
|--------|:-----:|:--------:|
| Health | 15 | 100% |
| Market Data | 38 | 100% |
| Account & Auth | 24 | 100% |
| Orders | 26 | 100% |
| Error Handling | 45 | 100% |
| **Total** | **148** | **95%** |

## Design Principles

- **Offline-first**: All tests use static fixtures — no network required
- **Contract-validated**: Every response schema is verified against the API reference
- **Edge-case rich**: Unicode, SQL injection, boundary values, empty payloads, rate limiting
- **Live mode**: Run with `pytest --live` against a real backend instance
- **Shared fixtures**: Auth tokens, mock API, parametrized helpers in `conftest.py`

## Running

```bash
# Default: offline mock tests
pytest tests/

# With coverage
pytest tests/ --cov=tests --cov-report=term

# Against a live backend
pytest tests/ --live

# Specific module
pytest tests/test_health.py -v
```
