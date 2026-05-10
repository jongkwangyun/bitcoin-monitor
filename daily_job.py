"""
GitHub Actions / 로컬 예약 실행용: 스냅샷 저장 + 텔레그램 요약 + 돌파 알림.
"""

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

_ROOT = Path(__file__).resolve().parent
load_dotenv(_ROOT / ".env")

from btc_monitor.config import DEFAULT_MARKET
from btc_monitor.persistence import save_snapshot
from btc_monitor.ma_chart import render_ma_chart_png
from btc_monitor.report import format_cross_alert, format_snapshot_html
from btc_monitor.snapshot import build_snapshot_full, cross_signature_from_snapshot
from btc_monitor.telegram_client import send_telegram_html, send_telegram_photo


def load_alert_cache(path: str) -> dict:
    if not os.path.isfile(path):
        return {"cross_signatures": []}
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data.get("cross_signatures"), list):
            data["cross_signatures"] = []
        return data
    except (json.JSONDecodeError, OSError):
        return {"cross_signatures": []}


def save_alert_cache(path: str, data: dict) -> None:
    sigs = list(data.get("cross_signatures", []))
    if len(sigs) > 40:
        data["cross_signatures"] = sigs[-40:]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=0)


def main() -> int:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    market = os.environ.get("UPBIT_MARKET", DEFAULT_MARKET).strip() or DEFAULT_MARKET

    if not token or not chat_id:
        print("TELEGRAM_BOT_TOKEN 과 TELEGRAM_CHAT_ID 를 설정하세요.", file=sys.stderr)
        return 1

    s, prev_row, curr_row, df_live = build_snapshot_full(market=market)
    save_snapshot(s)

    send_telegram_html(format_snapshot_html(s), token=token, chat_id=chat_id)
    chart_png = render_ma_chart_png(df_live, market)
    send_telegram_photo(
        chart_png,
        caption="<b>BTC 이동평균</b>\n일봉 종가(막대 구간은 최종 봉만 실시간가 반영)",
        token=token,
        chat_id=chat_id,
    )

    cache_path = os.environ.get("BTC_ALERT_CACHE", str(_ROOT / ".btc_alert_cache.json")).strip()
    cache = load_alert_cache(cache_path)
    sent: set[str] = set(cache.get("cross_signatures", []))
    wrote_cache = False

    for ev in s.crosses:
        sig = cross_signature_from_snapshot(s, ev)
        if sig in sent:
            continue
        msg = format_cross_alert(
            s,
            ev,
            float(prev_row["trade_price"]),
            float(curr_row["trade_price"]),
        )
        send_telegram_html(msg, token=token, chat_id=chat_id)
        sent.add(sig)
        cache["cross_signatures"] = list(sent)
        wrote_cache = True

    if wrote_cache:
        save_alert_cache(cache_path, cache)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
