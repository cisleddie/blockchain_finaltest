"""
Web 백엔드 (MCP 클라이언트 역할)
================================

브라우저 UI 는 이 Starlette 백엔드를 호출하고,
이 백엔드가 'MCP 클라이언트'가 되어 MCP 서버의 도구를 호출한다.

  Browser UI -> Starlette 백엔드 -> MCP ClientSession -> MCP 서버 -> Upbit API

즉 웹 UI 는 단순 정적 대시보드가 아니라, 실제 MCP 흐름을 그대로 태운다.
요청마다 stdio 로 서버 세션을 열고 call_tool() 한 뒤 결과를 JSON 으로 돌려준다.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse
from starlette.routing import Route

BASE = Path(__file__).resolve().parent
SERVER = str(BASE / "servers" / "upbit_server.py")
INDEX = str(BASE / "web" / "index.html")


async def _call_tool(name: str, args: dict) -> dict:
    """MCP 서버에 연결해 도구 1개를 호출하고 결과 텍스트와 메타데이터를 반환."""
    # env={**os.environ} 로 UPBIT_INSECURE 등 환경변수를 서버 프로세스에 전달
    params = StdioServerParameters(
        command=sys.executable, args=[SERVER], env={**os.environ}
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            listed = await session.list_tools()
            discovered = [t.name for t in listed.tools]
            result = await session.call_tool(name, args)
            text = "\n".join(b.text for b in result.content if b.type == "text")
            return {
                "server": "upbit",
                "tool": name,
                "arguments": args,
                "discovered_tools": discovered,
                "result": text,
            }


# --- API 라우트 --------------------------------------------------------------
async def index(request: Request):
    return FileResponse(INDEX)


async def list_tools(request: Request):
    out = await _call_tool("get_market_codes", {"quote": "KRW", "limit": 1})
    return JSONResponse({"server": "upbit", "tools": out["discovered_tools"]})


async def ticker(request: Request):
    market = request.query_params.get("market", "KRW-BTC")
    return JSONResponse(await _call_tool("get_ticker", {"market": market}))


async def orderbook(request: Request):
    market = request.query_params.get("market", "KRW-BTC")
    depth = int(request.query_params.get("depth", 5))
    return JSONResponse(await _call_tool("get_orderbook", {"market": market, "depth": depth}))


async def candles(request: Request):
    market = request.query_params.get("market", "KRW-BTC")
    interval = request.query_params.get("interval", "days")
    count = int(request.query_params.get("count", 5))
    return JSONResponse(
        await _call_tool("get_candles", {"market": market, "interval": interval, "count": count})
    )


async def trades(request: Request):
    market = request.query_params.get("market", "KRW-BTC")
    count = int(request.query_params.get("count", 10))
    return JSONResponse(await _call_tool("get_recent_trades", {"market": market, "count": count}))


async def markets(request: Request):
    quote = request.query_params.get("quote", "KRW")
    limit = int(request.query_params.get("limit", 30))
    return JSONResponse(await _call_tool("get_market_codes", {"quote": quote, "limit": limit}))


app = Starlette(
    routes=[
        Route("/", index),
        Route("/api/tools", list_tools),
        Route("/api/ticker", ticker),
        Route("/api/orderbook", orderbook),
        Route("/api/candles", candles),
        Route("/api/trades", trades),
        Route("/api/markets", markets),
    ]
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8765)
