"""
Upbit MCP Server
================

업비트(Upbit) 공개 시세(Quotation) API를 'MCP 도구(tool)'로 노출하는 MCP 서버.

- 인증 키가 필요 없는 '시세 조회' 엔드포인트만 사용한다(공개 API).
- 각 함수는 @mcp.tool() 로 등록되어, MCP 클라이언트가
  list_tools() 로 발견하고 call_tool() 로 호출할 수 있다.

핵심 엔드포인트(https://api.upbit.com):
  GET /v1/market/all                마켓 코드 목록
  GET /v1/ticker?markets=KRW-BTC    현재가(복수: markets)
  GET /v1/orderbook?markets=KRW-BTC 호가/주문장(복수: markets)
  GET /v1/candles/{unit}?market=... 캔들    (단수: market)
  GET /v1/trades/ticks?market=...   최근 체결(단수: market)

주의: ticker/orderbook 은 파라미터 이름이 'markets'(복수),
      candles/trades 는 'market'(단수)이다. (업비트 API의 실제 규약)
"""

from __future__ import annotations

import os

import httpx
from mcp.server.fastmcp import FastMCP

UPBIT_BASE = "https://api.upbit.com/v1"
TIMEOUT = 10.0

# 학교/회사망이 TLS 를 가로채 자체 서명 인증서를 끼워 넣는 경우,
# UPBIT_INSECURE=1 로 인증서 검증을 끌 수 있다(공개 시세 API 전용, 인증키 없음).
VERIFY_SSL = os.environ.get("UPBIT_INSECURE", "").lower() not in ("1", "true", "yes", "on")

mcp = FastMCP("upbit")


# ---------------------------------------------------------------------------
# 내부 헬퍼
# ---------------------------------------------------------------------------
def _normalize_market(market: str) -> str:
    """'btc' -> 'KRW-BTC' 처럼 사용자 입력을 업비트 마켓 코드로 정규화.

    - 'KRW-BTC' 같이 '-' 가 들어있으면 대문자로만 바꿔 그대로 사용
    - 'btc' 처럼 코인 심볼만 주면 기본 마켓을 KRW 로 가정
    """
    m = market.strip().upper()
    if "-" in m:
        return m
    return f"KRW-{m}"


async def _get(path: str, params: dict) -> object:
    """업비트 공개 API GET 요청 공통 처리."""
    url = f"{UPBIT_BASE}{path}"
    async with httpx.AsyncClient(timeout=TIMEOUT, verify=VERIFY_SSL) as client:
        resp = await client.get(url, params=params, headers={"Accept": "application/json"})
        resp.raise_for_status()
        return resp.json()


def _fmt_krw(value: float) -> str:
    """숫자를 천 단위 콤마가 있는 문자열로."""
    try:
        return f"{value:,.0f}" if abs(value) >= 100 else f"{value:,.4f}"
    except (TypeError, ValueError):
        return str(value)


# ---------------------------------------------------------------------------
# MCP 도구(tool) 정의
# ---------------------------------------------------------------------------
@mcp.tool()
async def get_market_codes(quote: str = "KRW", limit: int = 30) -> str:
    """업비트에서 거래 가능한 마켓 코드 목록을 조회한다.

    Args:
        quote: 기준 통화 필터. 'KRW', 'BTC', 'USDT' 중 하나(기본 'KRW').
        limit: 반환할 최대 개수(기본 30).
    """
    try:
        data = await _get("/market/all", {"isDetails": "false"})
    except Exception as e:  # noqa: BLE001
        return f"[오류] 마켓 목록 조회 실패: {e}"

    quote = quote.strip().upper()
    rows = [d for d in data if d["market"].startswith(f"{quote}-")][:limit]
    if not rows:
        return f"[안내] '{quote}' 마켓을 찾지 못했습니다."

    lines = [f"업비트 {quote} 마켓 (상위 {len(rows)}개)"]
    for d in rows:
        lines.append(f"  - {d['market']:<12} {d.get('korean_name', '')}")
    return "\n".join(lines)


@mcp.tool()
async def get_ticker(market: str) -> str:
    """단일 코인의 현재가(시세) 정보를 조회한다.

    Args:
        market: 마켓 코드 또는 심볼. 예) 'KRW-BTC', 'btc', 'eth'
    """
    code = _normalize_market(market)
    try:
        data = await _get("/ticker", {"markets": code})
    except Exception as e:  # noqa: BLE001
        return f"[오류] 현재가 조회 실패({code}): {e}"

    if not data:
        return f"[안내] '{code}' 시세를 찾지 못했습니다."

    t = data[0]
    rate = t["signed_change_rate"] * 100
    sign = "+" if rate >= 0 else ""
    return (
        f"[현재가] {t['market']}\n"
        f"  현재가      : {_fmt_krw(t['trade_price'])}\n"
        f"  전일 대비    : {sign}{rate:.2f}%  ({_fmt_krw(t['signed_change_price'])})\n"
        f"  당일 고가/저가: {_fmt_krw(t['high_price'])} / {_fmt_krw(t['low_price'])}\n"
        f"  24h 누적 거래대금: {_fmt_krw(t['acc_trade_price_24h'])}\n"
        f"  24h 누적 거래량  : {t['acc_trade_volume_24h']:,.4f}"
    )


@mcp.tool()
async def get_orderbook(market: str, depth: int = 5) -> str:
    """호가창(주문장, orderbook)의 매수/매도 호가를 조회한다.

    Args:
        market: 마켓 코드 또는 심볼. 예) 'KRW-BTC', 'btc'
        depth: 표시할 호가 단계 수(기본 5).
    """
    code = _normalize_market(market)
    try:
        data = await _get("/orderbook", {"markets": code})
    except Exception as e:  # noqa: BLE001
        return f"[오류] 호가 조회 실패({code}): {e}"

    if not data:
        return f"[안내] '{code}' 호가를 찾지 못했습니다."

    ob = data[0]
    units = ob["orderbook_units"][:depth]
    lines = [
        f"[호가창] {ob['market']}  (총매도 {ob['total_ask_size']:.4f} / 총매수 {ob['total_bid_size']:.4f})",
        f"  {'매도호가(ask)':>18}  {'잔량':>12}  |  {'매수호가(bid)':>14}  {'잔량':>12}",
    ]
    for u in units:
        lines.append(
            f"  {_fmt_krw(u['ask_price']):>18}  {u['ask_size']:>12.4f}  |  "
            f"{_fmt_krw(u['bid_price']):>14}  {u['bid_size']:>12.4f}"
        )
    # 최우선 호가 스프레드
    best_ask = units[0]["ask_price"]
    best_bid = units[0]["bid_price"]
    spread = best_ask - best_bid
    lines.append(f"  스프레드(최우선 매도-매수): {_fmt_krw(spread)}")
    return "\n".join(lines)


@mcp.tool()
async def get_candles(market: str, interval: str = "days", count: int = 5) -> str:
    """OHLCV 캔들(봉) 데이터를 조회한다.

    Args:
        market: 마켓 코드 또는 심볼. 예) 'KRW-BTC', 'btc'
        interval: 'days', 'weeks', 'months', 또는 분봉('1','3','5','15','30','60','240').
        count: 가져올 캔들 개수(기본 5, 최대 200).
    """
    code = _normalize_market(market)
    iv = interval.strip().lower()
    if iv in {"1", "3", "5", "10", "15", "30", "60", "240"}:
        path = f"/candles/minutes/{iv}"
        label = f"{iv}분봉"
    elif iv in {"days", "day", "d"}:
        path, label = "/candles/days", "일봉"
    elif iv in {"weeks", "week", "w"}:
        path, label = "/candles/weeks", "주봉"
    elif iv in {"months", "month", "m"}:
        path, label = "/candles/months", "월봉"
    else:
        return f"[안내] 지원하지 않는 interval: {interval}"

    try:
        data = await _get(path, {"market": code, "count": min(count, 200)})
    except Exception as e:  # noqa: BLE001
        return f"[오류] 캔들 조회 실패({code}): {e}"

    if not data:
        return f"[안내] '{code}' 캔들을 찾지 못했습니다."

    lines = [f"[캔들 {label}] {code}  (최근 {len(data)}개)"]
    lines.append(f"  {'시각(KST)':<20} {'시가':>12} {'고가':>12} {'저가':>12} {'종가':>12}")
    for c in data:
        ts = c["candle_date_time_kst"].replace("T", " ")
        lines.append(
            f"  {ts:<20} {_fmt_krw(c['opening_price']):>12} {_fmt_krw(c['high_price']):>12} "
            f"{_fmt_krw(c['low_price']):>12} {_fmt_krw(c['trade_price']):>12}"
        )
    return "\n".join(lines)


@mcp.tool()
async def get_recent_trades(market: str, count: int = 10) -> str:
    """최근 체결 내역(체결가, 체결량, 매수/매도)을 조회한다.

    Args:
        market: 마켓 코드 또는 심볼. 예) 'KRW-BTC', 'btc'
        count: 가져올 체결 개수(기본 10, 최대 500).
    """
    code = _normalize_market(market)
    try:
        data = await _get("/trades/ticks", {"market": code, "count": min(count, 500)})
    except Exception as e:  # noqa: BLE001
        return f"[오류] 체결 내역 조회 실패({code}): {e}"

    if not data:
        return f"[안내] '{code}' 체결 내역을 찾지 못했습니다."

    lines = [f"[최근 체결] {code}  (최근 {len(data)}건)"]
    lines.append(f"  {'시각(UTC)':<12} {'체결가':>14} {'체결량':>14} {'구분':>6}")
    for d in data:
        side = "매수" if d["ask_bid"] == "BID" else "매도"
        lines.append(
            f"  {d['trade_time_utc']:<12} {_fmt_krw(d['trade_price']):>14} "
            f"{d['trade_volume']:>14.6f} {side:>6}"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    # stdio 트랜스포트로 MCP 서버 실행 (클라이언트가 표준입출력으로 연결)
    mcp.run(transport="stdio")
