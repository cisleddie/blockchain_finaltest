# Upbit MCP 데모 — 사용 설명서

업비트(Upbit) 공개 시세 API를 **MCP(Model Context Protocol) 서버의 도구(tool)** 로 노출하고,
**MCP 클라이언트**가 그 도구를 `list_tools()` 로 발견하고 `call_tool()` 로 호출하는 프로그램입니다.

> 핵심: "서버만 만든 것"이 아니라 **MCP 클라이언트와 서버를 분리**했고, 도구 발견(discovery)과 호출(invocation)을 실제로 시연합니다.

---

## 1. 무엇을 하는가

- **MCP 서버**(`servers/upbit_server.py`)가 업비트 데이터를 5개 도구로 제공합니다.
  - 현재가, 호가창(주문장), 캔들(OHLCV), 최근 체결, 마켓 목록
- **MCP 클라이언트**(`clients/test_mcp_client.py`, CLI)가 서버에 연결해 도구를 발견하고 호출합니다.
- **웹 UI**(`web/index.html` + `web_app.py`)는 같은 흐름을 브라우저에서 보여줍니다. 백엔드(Starlette)가 곧 MCP 클라이언트입니다.

업비트 **시세(Quotation) API는 인증 키가 필요 없습니다.** (별도 API Key 발급 불필요)

---

## 2. 동작 흐름

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
├── servers/
│   └── upbit_server.py        # MCP 서버 (도구 5개 정의)
├── clients/
│   └── test_mcp_client.py     # MCP 클라이언트 (CLI 데모)
├── web/
│   └── index.html             # 브라우저 데모 콘솔
├── web_app.py                 # 웹 백엔드 (= MCP 클라이언트 역할)
├── docs/
│   └── demo_script_kr.md      # 발표/시연 스크립트
├── 사용설명서.md               # 이 문서
├── README.md                  # 영문 요약(GitHub용)
├── pyproject.toml             # uv 의존성
├── requirements.txt           # pip 의존성
├── run_demo.sh / run_ui.sh    # 실행 스크립트 (Mac/Linux/WSL 용)
└── .gitignore
```

---

## 4. 실행 환경

- Python **3.11 이상**
- 인터넷 연결 (실시간 API 호출)
- OS: Windows / macOS / Linux 모두 가능 (아래는 **Windows 기준** 우선)

---

## 5. 설치

압축을 푼 폴더(예: `D:\blockchain_finaltest`)에서 진행합니다.

### Windows (PowerShell)

```powershell
cd D:\blockchain_finaltest
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

> `Activate.ps1` 실행이 정책 때문에 막히면, PowerShell에서 한 번만:
> `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` 후 다시 활성화하거나,
> 가상환경 없이 곧바로 `pip install -r requirements.txt` 로 설치해도 됩니다.

### macOS / Linux / WSL

```bash
cd mcp-upbit-demo
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# uv 사용 시: uv sync
```

---

## 6. 실행 방법

이 프로그램은 학교/회사망이 TLS 트래픽을 검사하는 환경에서 SSL 인증서 오류가 날 수 있어,
**`UPBIT_INSECURE=1`** 환경변수로 인증서 검증을 끌 수 있습니다(공개 시세 API 전용).
일반 인터넷 환경이면 이 변수 없이도 동작합니다.

### 6-1. CLI 데모 (서버/클라이언트 분리 시연 — 핵심)

**Windows (PowerShell)**

```powershell
$env:UPBIT_INSECURE=1
python clients/test_mcp_client.py KRW-BTC
```

다른 코인을 보려면 마켓 코드만 바꿉니다.

```powershell
python clients/test_mcp_client.py KRW-ETH
python clients/test_mcp_client.py btc        # 심볼만 주면 KRW 마켓으로 간주
python clients/test_mcp_client.py KRW-BTC --verbose   # 내부 MCP/HTTP 로그까지 표시
```

**Windows (명령 프롬프트 CMD)**

```cmd
set UPBIT_INSECURE=1
python clients/test_mcp_client.py KRW-BTC
```

**macOS / Linux / WSL**

```bash
UPBIT_INSECURE=1 python clients/test_mcp_client.py KRW-BTC
# 또는: ./run_demo.sh KRW-BTC
```

출력은 다음 3단계로 나타납니다.

```text
[1/3] MCP 세션 초기화
[2/3] 도구 발견 (list_tools)
[3/3] 도구 호출 (call_tool)
```

### 6-2. 웹 UI

**Windows (PowerShell)**

```powershell
$env:UPBIT_INSECURE=1
python -m uvicorn web_app:app --host 127.0.0.1 --port 8765
```

**macOS / Linux / WSL**

```bash
UPBIT_INSECURE=1 python -m uvicorn web_app:app --host 127.0.0.1 --port 8765
# 또는: ./run_ui.sh
```

실행 후 브라우저에서 접속:

```text
http://127.0.0.1:8765
```

버튼(현재가 / 호가창 / 캔들 / 최근 체결 / 마켓 목록 / 도구 발견)을 누르면
화면에 **server · tool · arguments · discovered tools · result** 가 함께 표시됩니다.

---

## 7. MCP 도구 목록

파일: `servers/upbit_server.py`

| 도구 | 설명 | 업비트 엔드포인트 |
|---|---|---|
| `get_market_codes(quote, limit)` | 거래 가능한 마켓 코드 목록 | `GET /v1/market/all` |
| `get_ticker(market)` | 현재가, 전일 대비, 고저가, 거래대금 | `GET /v1/ticker?markets=` |
| `get_orderbook(market, depth)` | 호가창(매수/매도 호가·잔량), 스프레드 | `GET /v1/orderbook?markets=` |
| `get_candles(market, interval, count)` | OHLCV 캔들(일/주/월/분봉) | `GET /v1/candles/{interval}?market=` |
| `get_recent_trades(market, count)` | 최근 체결가·체결량·매수/매도 | `GET /v1/trades/ticks?market=` |

- `market` 인자는 `KRW-BTC` 같은 마켓 코드 또는 `btc` 같은 심볼을 받습니다(심볼만 주면 KRW 마켓으로 간주).
- **업비트 API 규약 주의:** 현재가/호가는 파라미터 이름이 `markets`(복수), 캔들/체결은 `market`(단수)입니다. 서버 코드에 그대로 반영되어 있습니다.

---

## 8. 실제 실행 결과 예시

`python clients/test_mcp_client.py KRW-BTC` 실행 시 출력 예시입니다.

```text
============================================================
Upbit MCP 클라이언트 데모
============================================================
[1/3] MCP 세션 초기화 (stdio 로 서버 연결)
      -> 세션 초기화 완료
[2/3] 도구 발견 (list_tools)
      - get_market_codes     : 업비트에서 거래 가능한 마켓 코드 목록을 조회한다.
      - get_ticker           : 단일 코인의 현재가(시세) 정보를 조회한다.
      - get_orderbook        : 호가창(주문장, orderbook)의 매수/매도 호가를 조회한다.
      - get_candles          : OHLCV 캔들(봉) 데이터를 조회한다.
      - get_recent_trades    : 최근 체결 내역(체결가, 체결량, 매수/매도)을 조회한다.
[3/3] 도구 호출 (call_tool)  대상 마켓: KRW-BTC
  >> call_tool(get_ticker, {'market': 'KRW-BTC'})
     [현재가] KRW-BTC
       현재가      : 102,300,000
       전일 대비    : -1.77%  (-1,840,000)
       당일 고가/저가: 104,140,000 / 102,300,000
       24h 누적 거래대금: 319,355,456,014
       24h 누적 거래량  : 3,030.9675
  >> call_tool(get_orderbook, {'market': 'KRW-BTC', 'depth': 5})
     [호가창] KRW-BTC  (총매도 7.3907 / 총매수 1.1712)
       ... (매도/매수 5단계 호가 + 스프레드)
  >> call_tool(get_candles, {'market': 'KRW-BTC', 'interval': 'days', 'count': 3})
     [캔들 일봉] KRW-BTC  (최근 3개)
       ... (시가/고가/저가/종가)
  >> call_tool(get_recent_trades, {'market': 'KRW-BTC', 'count': 5})
     [최근 체결] KRW-BTC  (최근 5건)
       ... (체결가/체결량/매수·매도)
============================================================
데모 종료
============================================================
```

`[2/3]`에서 클라이언트가 서버의 도구를 **발견**하고, `[3/3]`에서 실제로 **호출**해 업비트 실데이터를 받아오는 것이 확인됩니다.

---

## 9. 과제 요구사항 충족 체크리스트

- [x] MCP 서버 **1개 이상** → `servers/upbit_server.py`
- [x] MCP 도구 **2개 이상** → 5개 제공
- [x] 클라이언트에서 `list_tools()` 로 도구 발견
- [x] 클라이언트에서 `call_tool()` 로 도구 호출
- [x] **Upbit** 코인 가격 / **호가창(주문장)** / 관련 정보(캔들·체결·마켓) 조회
- [x] 사용 설명서/문서 (이 문서 + `docs/demo_script_kr.md`)

---

## 10. 동작 확인(스모크 테스트)

문법 검사:

```bash
python -m py_compile servers/upbit_server.py clients/test_mcp_client.py web_app.py
```

업비트 시세 API 직접 확인(서버 없이, 인터넷·API 상태 점검용):

```bash
curl "https://api.upbit.com/v1/ticker?markets=KRW-BTC"
```

웹 서버 실행 후 API 직접 호출:

```bash
curl http://127.0.0.1:8765/api/tools
curl "http://127.0.0.1:8765/api/ticker?market=KRW-BTC"
```

---

## 11. 트러블슈팅

### SSL 인증서 오류 (`CERTIFICATE_VERIFY_FAILED ... self-signed certificate`)
학교/회사망이 TLS를 가로채면서 자체 서명 인증서를 끼워 넣어 발생합니다. 코드 문제가 아닙니다.
실행 시 `UPBIT_INSECURE=1` 을 설정하면 인증서 검증을 끄고 동작합니다(위 6번 참고).
공개 시세 데이터만 읽고 인증키를 쓰지 않으므로 수업 데모 용도로는 무방합니다.

### `python` 을 찾을 수 없음
Windows에서 `python` 대신 `py` 를 써 보세요. 예) `py clients/test_mcp_client.py KRW-BTC`

### 포트 8765 사용 중
다른 포트로 실행하세요.

```powershell
python -m uvicorn web_app:app --host 127.0.0.1 --port 8766
```

### 외부 API 호출 실패 (네트워크 차단 등)
업비트 API가 막혀 있어도 **MCP 구조 자체는 정상 동작**합니다.
이 경우 도구 결과에 `[오류] ... 조회 실패` 가 표시되며, 세션 초기화와
도구 발견(`list_tools`)·호출(`call_tool`)은 그대로 확인됩니다.
즉 "MCP 배선은 정상이고 외부 API 호출만 실패"한 상태입니다.

### 업비트 요청 한도(Rate limit)
공개 시세 API에도 호출 한도가 있습니다. 짧은 시간에 너무 많이 호출하면
`429` 가 날 수 있으니 잠시 후 다시 시도하세요.

---

## 12. 환경변수 정리

| 변수 | 값 | 효과 |
|---|---|---|
| `UPBIT_INSECURE` | `1` / `true` | SSL 인증서 검증을 끔 (학교/회사망 TLS 가로채기 대응) |
| (미설정) | — | 기본값: 인증서 검증 켬(보안 기본) |

PowerShell에서 설정한 `$env:UPBIT_INSECURE=1` 은 **그 창에서만** 유효합니다. 새 창을 열면 다시 설정하세요.
