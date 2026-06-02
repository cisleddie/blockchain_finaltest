#!/usr/bin/env bash
# 웹 UI 서버 실행 (브라우저에서 http://127.0.0.1:8765 접속)
set -e
unset VIRTUAL_ENV
# 학교/회사망 TLS 가로채기로 인한 SSL 인증서 오류 무시 (공개 시세 API 전용)
export UPBIT_INSECURE=1
if command -v uv >/dev/null 2>&1; then
  uv run uvicorn web_app:app --host 127.0.0.1 --port 8765
else
  python -m uvicorn web_app:app --host 127.0.0.1 --port 8765
fi
