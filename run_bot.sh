#!/usr/bin/env bash
# run_bot.sh — bot.py 실행 (systemd ExecStart 용)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

export LANG="ko_KR.UTF-8"
export LC_ALL="ko_KR.UTF-8"
export TZ="Asia/Seoul"
export PYTHONUNBUFFERED=1

exec "$SCRIPT_DIR/venv/bin/python3" "$SCRIPT_DIR/bot.py"
