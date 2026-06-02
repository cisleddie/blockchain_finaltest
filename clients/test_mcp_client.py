"""
Upbit MCP Client (CLI 데모)
===========================

이 클라이언트는 'MCP 클라이언트' 역할을 보여준다.

  1) stdio 로 MCP 서버(servers/upbit_server.py) 프로세스를 띄우고 세션을 연다
  2) list_tools() 로 서버가 제공하는 도구 목록을 '발견'한다
  3) call_tool() 로 실제 도구를 '호출'하고 결과를 받는다

이것이 '서버만 만든 것'이 아니라 '클라이언트와 서버를 분리'했다는 증거다.

사용법:
  python clients/test_mcp_client.py                 # 기본: KRW-BTC 데모
  python clients/test_mcp_client.py KRW-ETH         # 다른 코인
  python clients/test_mcp_client.py btc --verbose   # 내부 로그까지 표시
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# 서버 스크립트 절대 경로
SERVER = str(Path(__file__).resolve().parent.parent / "servers" / "upbit_server.py")


def _quiet_logs() -> None:
    """수업 시연용: MCP/HTTP 내부 로그를 숨겨 흐름에 집중하게 한다."""
    for name in ("mcp", "httpx", "httpcore", "asyncio"):
        logging.getLogger(name).setLevel(logging.CRITICAL)


async def run(market: str, verbose: bool) -> None:
    # 서버를 자식 프로세스로 실행. env={**os.environ} 로 UPBIT_INSECURE 등
    # 현재 셸의 환경변수를 서버까지 전달한다(MCP 기본값은 대부분을 걸러내므로 명시 전달).
    params = StdioServerParameters(
        command=sys.executable, args=[SERVER], env={**os.environ}
    )

    print("=" * 60)
    print("Upbit MCP 클라이언트 데모")
    print("=" * 60)

    print("\n[1/3] MCP 세션 초기화 (stdio 로 서버 연결)")
    # quiet 모드에서는 서버 프로세스의 stderr(내부 로그)를 /dev/null 로 버린다
    devnull = open(os.devnull, "w") if not verbose else None
    errlog = devnull if devnull is not None else sys.stderr
    async with stdio_client(params, errlog=errlog) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("      -> 세션 초기화 완료")

            print("\n[2/3] 도구 발견 (list_tools)")
            tools = await session.list_tools()
            for t in tools.tools:
                summary = (t.description or "").strip().splitlines()[0]
                print(f"      - {t.name:<20} : {summary}")

            print(f"\n[3/3] 도구 호출 (call_tool)  대상 마켓: {market}")

            calls = [
                ("get_ticker", {"market": market}),
                ("get_orderbook", {"market": market, "depth": 5}),
                ("get_candles", {"market": market, "interval": "days", "count": 3}),
                ("get_recent_trades", {"market": market, "count": 5}),
            ]
            for name, args in calls:
                print(f"\n  >> call_tool({name}, {args})")
                result = await session.call_tool(name, args)
                text = "\n".join(
                    block.text for block in result.content if block.type == "text"
                )
                # 보기 좋게 들여쓰기
                for line in text.splitlines():
                    print(f"     {line}")

    print("\n" + "=" * 60)
    print("데모 종료")
    print("=" * 60)
    if devnull is not None:
        devnull.close()


def main() -> None:
    args = [a for a in sys.argv[1:]]
    verbose = "--verbose" in args
    args = [a for a in args if a != "--verbose"]
    market = args[0] if args else "KRW-BTC"

    if not verbose:
        _quiet_logs()

    asyncio.run(run(market, verbose))


if __name__ == "__main__":
    main()
