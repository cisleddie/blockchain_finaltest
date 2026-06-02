# 발표/시연 스크립트 (기말 과제)

목표: "서버만 만든 게 아니라, **MCP 클라이언트와 서버를 분리**했고, 도구 발견과 호출을 실제로 보여준다"를 증명.

소요 시간: 약 3~5분

---

## 0. 준비 (발표 전에 미리)

```bash
cd mcp-upbit-demo
uv sync          # 또는 pip install -r requirements.txt
```

인터넷 연결 확인:

```bash
curl 'https://api.upbit.com/v1/ticker?markets=KRW-BTC'
```

---

## 1. 구조 설명 (30초)

- MCP **서버**: 업비트 데이터를 '도구'로 노출 (`servers/upbit_server.py`)
- MCP **클라이언트**: 도구를 발견(`list_tools`)하고 호출(`call_tool`) (`clients/test_mcp_client.py`)
- 둘은 **stdio** 로 분리된 프로세스로 통신

화면에 README_KR.md 의 "전체 흐름" 다이어그램을 띄워 설명.

---

## 2. CLI 데모 (1분)

```bash
./run_demo.sh KRW-BTC
```

말할 포인트:
- `[1/3]` 클라이언트가 서버 프로세스를 띄우고 세션을 초기화
- `[2/3]` `list_tools()` 결과로 5개 도구가 나열됨 → **도구 발견**
- `[3/3]` `call_tool()` 로 현재가/호가/캔들/체결을 실제 호출 → **도구 호출**

내부 동작을 보여주려면:

```bash
./run_demo.sh KRW-ETH --verbose   # MCP/HTTP 내부 로그 표시
```

---

## 3. 서버 코드 보여주기 (40초)

`servers/upbit_server.py` 에서:
- `@mcp.tool()` 데코레이터로 함수가 도구로 등록되는 부분
- `get_ticker`, `get_orderbook` 가 업비트 엔드포인트를 호출하는 부분
- 현재가/호가는 `markets`(복수), 캔들/체결은 `market`(단수) 차이 강조

---

## 4. 클라이언트 코드 보여주기 (40초)

`clients/test_mcp_client.py` 에서:
- `stdio_client(...)` 로 서버에 연결
- `session.list_tools()` (발견)
- `session.call_tool(name, args)` (호출)

---

## 5. 웹 UI 데모 (1분)

```bash
./run_ui.sh
```

브라우저 `http://127.0.0.1:8765` 접속 후:
- "도구 발견" 버튼 → `list_tools()` 결과 표시
- "현재가"/"호가창" 버튼 → server / tool / arguments / discovered tools / result 가 함께 보임
- 백엔드(`web_app.py`)가 곧 MCP 클라이언트임을 설명

---

## 6. 마무리 (20초)

- 과제 요구사항 충족: 서버 1개, 도구 5개(>=2), `list_tools()`/`call_tool()` 검증, Upbit 가격·호가·관련 정보
- 외부 API가 막혀도 MCP 구조는 정상 동작함을 한 줄로 언급

---

## 예상 질문 대비

- **Q. 왜 인증 키가 없나요?**
  업비트의 시세(Quotation) API는 공개 API라 키가 필요 없습니다. 주문/잔고 등 거래 API만 JWT 인증이 필요합니다.

- **Q. MCP 서버와 일반 REST 서버의 차이?**
  MCP 서버는 기능을 표준화된 '도구(tool)' 스키마로 노출하고, 클라이언트가 `list_tools()` 로 동적으로 발견할 수 있습니다. 일반 REST는 엔드포인트를 미리 알아야 합니다.

- **Q. stdio 외에 다른 전송 방식?**
  MCP 는 stdio 외에 HTTP/SSE 전송도 지원합니다. 이 데모는 교육용으로 가장 단순한 stdio 를 사용합니다.
