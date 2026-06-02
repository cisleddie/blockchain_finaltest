#!/usr/bin/env bash
# CLI MCP 데모 실행: 세션 초기화 -> 도구 발견 -> 도구 호출
set -e
unset VIRTUAL_ENV
# 학교/회사망 TLS 가로채기로 인한 SSL 인증서 오류 무시 (공개 시세 API 전용)
export UPBIT_INSECURE=1
MARKET="${1:-KRW-BTC}"
if command -v uv >/dev/null 2>&1; then
  uv run python clients/test_mcp_client.py "$MARKET"
else
  python clients/test_mcp_client.py "$MARKET"
fi
