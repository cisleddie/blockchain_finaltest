# Upbit MCP Demo

An MCP (Model Context Protocol) demo where an **MCP client** discovers and calls tools exposed by an **MCP server** that wraps Upbit's public quotation API.

- **MCP server** (`servers/upbit_server.py`) exposes 5 tools: ticker, orderbook, candles, recent trades, market codes.
- **CLI client** (`clients/test_mcp_client.py`) demonstrates `stdio`, `list_tools()`, and `call_tool()`.
- **Web UI** (`web/index.html` + `web_app.py`) runs the same MCP flow in a browser; the Starlette backend acts as the MCP client.

Upbit's quotation (market data) API requires **no API key**.

## Flow

```text
User / Browser / CLI
  → MCP Client (CLI or web backend)
    → list_tools(), call_tool()
      → MCP Server (servers/upbit_server.py)
        → Upbit public API (api.upbit.com)
```

## Requirements

- Python 3.11+
- Internet access for live API calls

## Setup

```bash
# with uv
uv sync

# or with pip
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
# CLI demo
./run_demo.sh KRW-BTC
python clients/test_mcp_client.py btc --verbose

# Web UI -> http://127.0.0.1:8765
./run_ui.sh
```

## Tools

| Tool | Description | Endpoint |
|---|---|---|
| `get_market_codes(quote, limit)` | List tradable market codes | `/v1/market/all` |
| `get_ticker(market)` | Current price, 24h change, high/low, volume | `/v1/ticker?markets=` |
| `get_orderbook(market, depth)` | Bid/ask levels and spread | `/v1/orderbook?markets=` |
| `get_candles(market, interval, count)` | OHLCV candles | `/v1/candles/{interval}?market=` |
| `get_recent_trades(market, count)` | Recent executions | `/v1/trades/ticks?market=` |

> Note: Upbit uses `markets` (plural) for ticker/orderbook, but `market` (singular) for candles/trades.

See `README_KR.md` for the full Korean manual.
