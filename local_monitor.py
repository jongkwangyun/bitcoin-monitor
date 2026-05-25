"""
30분 간격 BTC 모니터링 루프 — Ubuntu Server systemd 데몬용.

기능:
- SIGTERM/SIGINT graceful shutdown
- 매 실행 후 gc.collect() (메모리 누수 방지)
- RotatingFileHandler 로그 (10MB × 5)
- 실행 시간 / 메모리 사용량 로깅
"""

import gc
import os
import signal
import sys
import time
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
import traceback

from btc_monitor.monitor import main as daily_job_main

_ROOT = Path(__file__).resolve().parent
_LOG_DIR = _ROOT / "logs"
_LOG_DIR.mkdir(exist_ok=True)

# ── 로깅 설정 ──────────────────────────────────────────────
_fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")

# stdout (systemd journald 연동)
_sh = logging.StreamHandler(sys.stdout)
_sh.setFormatter(_fmt)

# 파일 (10MB × 5 rotation)
_fh = RotatingFileHandler(
    _LOG_DIR / "monitor.log",
    maxBytes=10 * 1024 * 1024,
    backupCount=5,
    encoding="utf-8",
)
_fh.setFormatter(_fmt)

logging.basicConfig(level=logging.INFO, handlers=[_sh, _fh])
logger = logging.getLogger("local_monitor")

# ── Graceful shutdown ──────────────────────────────────────
_shutdown_requested = False


def _signal_handler(signum, frame):
    global _shutdown_requested
    sig_name = signal.Signals(signum).name
    logger.info("Received %s — shutting down gracefully…", sig_name)
    _shutdown_requested = True


signal.signal(signal.SIGTERM, _signal_handler)
signal.signal(signal.SIGINT, _signal_handler)


# ── 유틸리티 ───────────────────────────────────────────────
def _memory_mb() -> float:
    """현재 프로세스 RSS(MB). /proc 가 없으면 -1 반환."""
    try:
        with open("/proc/self/status") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    return int(line.split()[1]) / 1024.0
    except (FileNotFoundError, OSError):
        pass
    return -1.0


def get_seconds_until_next_period(minutes: int = 30) -> float:
    now = datetime.now()
    seconds_past_hour = now.minute * 60 + now.second + now.microsecond / 1_000_000
    period_seconds = minutes * 60
    next_period = ((seconds_past_hour // period_seconds) + 1) * period_seconds
    wait_seconds = next_period - seconds_past_hour
    return wait_seconds


# ── 메인 루프 ──────────────────────────────────────────────
def run():
    logger.info("Starting local monitor loop (30m interval)…")
    logger.info("PID=%d  Python=%s", os.getpid(), sys.version.split()[0])

    # 시작 시 즉시 1회 실행
    _run_once("initial")

    while not _shutdown_requested:
        wait_seconds = get_seconds_until_next_period(30)
        next_time = datetime.fromtimestamp(time.time() + wait_seconds)
        logger.info(
            "Waiting %.1f min until next check at %s",
            wait_seconds / 60,
            next_time.strftime("%H:%M:%S"),
        )

        # 대기 중에도 shutdown 신호를 감지하기 위해 짧은 간격으로 sleep
        deadline = time.monotonic() + wait_seconds
        while time.monotonic() < deadline:
            if _shutdown_requested:
                break
            time.sleep(min(1.0, deadline - time.monotonic()))

        if _shutdown_requested:
            break

        _run_once("scheduled")

    logger.info("Monitor loop stopped cleanly.")


def _run_once(label: str) -> None:
    logger.info("Running %s check…", label)
    t0 = time.monotonic()
    try:
        daily_job_main()
    except Exception as e:
        logger.error("Error in daily_job: %s", e)
        logger.error(traceback.format_exc())
    elapsed = time.monotonic() - t0
    mem = _memory_mb()
    mem_str = f"{mem:.1f}MB" if mem >= 0 else "N/A"
    logger.info("Check done in %.1fs  RSS=%s", elapsed, mem_str)

    # 명시적 GC — pandas/matplotlib 임시 객체 해제
    gc.collect()


if __name__ == "__main__":
    run()
