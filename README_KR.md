# Upbit MCP 데모 (기말 과제)

업비트(Upbit) 공개 시세 API를 **MCP(Model Context Protocol) 서버의 도구(tool)** 로 노출하고,
**MCP 클라이언트**가 그 도구를 `list_tools()` 로 발견하고 `call_tool()` 로 호출하는 것을 보여주는 프로젝트입니다.

> 핵심: "서버만 만든 것"이 아니라 **클라이언트와 서버를 분리**했고, 도구 발견(discovery)과 호출(invocation)을 실제로 시연합니다.

---

## 1. 무엇을 하는가

- **MCP 서버**(`servers/upbit_server.py`)가 업비트 데이터를 5개 도구로 제공합니다.
  - 현재가, 호가창(주문장), 캔들(OHLCV), 최근 체결, 마켓 목록
- **MCP 클라이언트**(`clients/test_mcp_client.py`, CLI)가 서버에 연결해 도구를 발견하고 호출합니다.
- **웹 UI**(`web/index.html` + `web_app.py`)는 같은 흐름을 브라우저에서 보여줍니다. 백엔드(Starlette)가 곧 MCP 클라이언트입니다.

업비트 **시세(Quotation) API는 인증 키가 필요 없습니다.** (별도 API Key 발급 불필요)

---

## 2. 전체 흐름

```text
사용자 / 브라우저 / CLI
  ↓ 요청
MCP 클라이언트 (CLI 또는 웹 백엔드)
  ↓ list_tools(), call_tool()
MCP 서버 (servers/upbit_server.py)
  ↓ 외부 API 요청
Upbit 공개 API (api.upbit.com)
  ↓ 결과
MCP 서버
  ↓ 도구 결과(tool result)
MCP 클라이언트 / UI
  ↓ 표시
사용자
```

---

## 3. 프로젝트 구조

```text
mcp-upbit-demo/
├── README.md                  # GitHub용(영문) 문서
├── README_KR.md               # 이 문서(한국어 사용 설명서)
├── pyproject.toml             # uv 용 의존성
├── requirements.txt           # pip 용 의존성(대안)
├── run_demo.sh                # CLI 데모 실행
├── run_ui.sh                  # 웹 UI 서버 실행
├── web_app.py                 # Starlette 백엔드(=MCP 클라이언트)
├── web/
│   └── index.html             # 브라우저 데모 콘솔
├── servers/
│   └── upbit_server.py        # Upbit MCP 서버 (도구 5개)
├── clients/
│   └── test_mcp_client.py     # CLI MCP 클라이언트 데모
└── docs/
    └── demo_script_kr.md      # 발표/시연 스크립트
```

---

## 4. 설치

Python **3.11 이상** 필요. 인터넷 연결 필요(실시간 API 호출).

### 방법 A — `uv` 사용 (권장, 교수님 데모와 동일)

```bash
cd mcp-upbit-demo
uv sync
```

### 방법 B — 표준 venv + pip

```bash
cd mcp-upbit-demo
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

## 5. 실행

### 5-1. CLI 데모 (서버/클라이언트 분리 시연)

```bash
./run_demo.sh                 # 기본 KRW-BTC
./run_demo.sh KRW-ETH         # 다른 코인
```

`uv` 없이 직접 실행:

```bash
python clients/test_mcp_client.py KRW-BTC
python clients/test_mcp_client.py btc --verbose   # 내부 MCP/HTTP 로그까지 표시
```

출력은 수업 시연에 맞춰 단계별로 보입니다.

```text
[1/3] MCP 세션 초기화
[2/3] 도구 발견 (list_tools)
[3/3] 도구 호출 (call_tool)
```

### 5-2. 웹 UI

```bash
./run_ui.sh
```

브라우저에서 접속:

```text
http://127.0.0.1:8765
```

버튼(현재가 / 호가창 / 캔들 / 최근 체결 / 마켓 목록 / 도구 발견)을 누르면
화면에 **server, tool, arguments, discovered tools, result** 가 함께 표시됩니다.

---

## 6. MCP 도구 목록

파일: `servers/upbit_server.py`

| 도구 | 설명 | 업비트 엔드포인트 |
|---|---|---|
| `get_market_codes(quote, limit)` | 거래 가능한 마켓 코드 목록 | `GET /v1/market/all` |
| `get_ticker(market)` | 현재가, 전일 대비, 고저가, 거래대금 | `GET /v1/ticker?markets=...` |
| `get_orderbook(market, depth)` | 호가창(매수/매도 호가·잔량), 스프레드 | `GET /v1/orderbook?markets=...` |
| `get_candles(market, interval, count)` | OHLCV 캔들(일/주/월/분봉) | `GET /v1/candles/{interval}?market=...` |
| `get_recent_trades(market, count)` | 최근 체결가·체결량·매수/매도 | `GET /v1/trades/ticks?market=...` |

- `market` 은 `KRW-BTC` 같은 마켓 코드 또는 `btc` 같은 심볼을 받습니다(심볼만 주면 KRW 마켓으로 간주).
- **주의(업비트 API 규약):** 현재가/호가는 파라미터 이름이 `markets`(복수), 캔들/체결은 `market`(단수)입니다. 서버 코드에 그대로 반영되어 있습니다.

---

## 7. 과제 요구사항 충족 체크리스트

- [x] MCP 서버 **1개 이상** → `servers/upbit_server.py`
- [x] MCP 도구 **2개 이상** → 5개 제공
- [x] 클라이언트에서 `list_tools()` 로 도구 발견
- [x] 클라이언트에서 `call_tool()` 로 도구 호출
- [x] **Upbit** 코인 가격 / **호가창(주문장)** / 관련 정보(캔들·체결·마켓) 조회
- [x] 사용 설명서/문서 (이 문서 + `docs/demo_script_kr.md`)

---

## 8. 동작 확인(스모크 테스트)

문법 검사:

```bash
python -m py_compile servers/upbit_server.py clients/test_mcp_client.py web_app.py
```

웹 서버 실행 후 API 직접 호출:

```bash
curl http://127.0.0.1:8765/api/tools
curl 'http://127.0.0.1:8765/api/ticker?market=KRW-BTC'
curl 'http://127.0.0.1:8765/api/orderbook?market=KRW-ETH&depth=5'
```

업비트 시세 API 직접 확인(서버 없이):

```bash
curl 'https://api.upbit.com/v1/ticker?markets=KRW-BTC'
```

---

## 9. 트러블슈팅

### 포트 8765 사용 중

```bash
# 사용 중인 프로세스 확인
ss -ltnp 'sport = :8765'
# 다른 포트로 실행
python -m uvicorn web_app:app --host 127.0.0.1 --port 8766
```

### `VIRTUAL_ENV` 경고 (uv)

`run_demo.sh` / `run_ui.sh` 는 `uv` 호출 전에 `VIRTUAL_ENV` 를 해제합니다. 수동 실행 시 경고가 보이면:

```bash
unset VIRTUAL_ENV
```

### 외부 API 호출 실패 (네트워크 차단 등)

업비트 API가 일시적으로 막혀 있어도 **MCP 구조 자체는 정상 동작**합니다.
이 경우 도구 결과에 `[오류] ... 조회 실패` 메시지가 표시되며, 세션 초기화와
도구 발견(`list_tools`)·호출(`call_tool`)은 그대로 확인됩니다.
즉 "MCP 배선은 정상이고 외부 API 호출만 실패"한 상태입니다.

### 업비트 요청 한도(Rate limit)

공개 시세 API에도 호출 한도가 있습니다. 짧은 시간에 너무 많이 누르면
`429` 가 날 수 있으니 잠시 후 다시 시도하세요.

---

## 10. 확장 아이디어 (선택)

- `compare_markets(markets)` : 여러 코인 현재가/등락률 비교
- `get_market_summary(quote)` : KRW 마켓 상위 거래대금 순위
- 분봉 데이터를 받아 간단한 이동평균/변동성 계산 도구 추가
- 업비트 WebSocket(실시간 ticker)으로 확장
