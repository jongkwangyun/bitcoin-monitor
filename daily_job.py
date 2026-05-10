"""
GitHub Actions / 로컬 예약 실행용: 스냅샷 저장 + 돌파 감지 알림 + 정기 리포트.
"""
import os
import sys
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

_ROOT = Path(__file__).resolve().parent
load_dotenv(_ROOT / ".env")

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("daily_job")

from btc_monitor.config import DEFAULT_MARKET
from btc_monitor.persistence import save_snapshot
from btc_monitor.ma_chart import render_ma_chart_png
from btc_monitor.report import format_snapshot_html
from btc_monitor.snapshot import build_snapshot_full
from btc_monitor.notifier import send_telegram_html, send_telegram_photo
from btc_monitor.signal_manager import load_alert_cache, save_alert_cache, check_ma_cross, get_positions
from btc_monitor.report_manager import should_send_regular_report, format_regular_report

def monitor_cross_signal(s, df_live, market, token, chat_id, cache_path):
    cache = load_alert_cache(cache_path)
    
    alerts_to_send = []
    live_price = float(s.live_price_krw)
    ma120 = float(s.ma120) if s.ma120 is not None else None
    ma200 = float(s.ma200) if s.ma200 is not None else None

    original_state_str = json.dumps(cache.get("ma_state", {}), sort_keys=True)

    msg_120 = check_ma_cross(cache, "120", ma120, live_price)
    if msg_120: alerts_to_send.append(msg_120)
        
    msg_200 = check_ma_cross(cache, "200", ma200, live_price)
    if msg_200: alerts_to_send.append(msg_200)

    new_state_str = json.dumps(cache.get("ma_state", {}), sort_keys=True)
    if original_state_str != new_state_str:
        save_alert_cache(cache_path, cache)

    if alerts_to_send:
        titles = "\n".join(alerts_to_send)
        snapshot_msg = format_snapshot_html(s)
        full_msg = f"{titles}\n\n{snapshot_msg}"
        
        logger.info("MA Cross confirmed! Sending telegram alert.")
        send_telegram_html(full_msg, token=token, chat_id=chat_id)
        
        chart_png = render_ma_chart_png(df_live, market)
        send_telegram_photo(
            chart_png,
            caption="<b>BTC 이동평균 돌파 알림</b>\n일봉 종가(막대 구간은 최종 봉만 실시간가 반영)",
            token=token,
            chat_id=chat_id,
        )

def maybe_send_regular_report(s, df_live, market, token, chat_id, report_state_path, p120_txt, p200_txt):
    if should_send_regular_report(report_state_path):
        logger.info("Sending regular scheduled report.")
        msg = format_regular_report(s, p120_txt, p200_txt)
        send_telegram_html(msg, token=token, chat_id=chat_id)
        
        chart_png = render_ma_chart_png(df_live, market)
        send_telegram_photo(
            chart_png,
            caption="<b>BTC 이동평균 (정기 리포트)</b>\n일봉 종가(막대 구간은 최종 봉만 실시간가 반영)",
            token=token,
            chat_id=chat_id,
        )

def main() -> int:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    market = os.environ.get("UPBIT_MARKET", DEFAULT_MARKET).strip() or DEFAULT_MARKET

    if not token or not chat_id:
        logger.error("TELEGRAM_BOT_TOKEN 과 TELEGRAM_CHAT_ID 를 설정하세요.")
        return 1

    try:
        s, prev_row, curr_row, df_live = build_snapshot_full(market=market)
    except Exception as e:
        logger.exception(f"API 호출 실패: {e}")
        return 1

    cache_path = os.environ.get("BTC_ALERT_CACHE", str(_ROOT / ".btc_alert_cache.json")).strip()
    report_state_path = os.environ.get("BTC_REPORT_CACHE", str(_ROOT / ".btc_report_state.json")).strip()

    live_price = float(s.live_price_krw)
    ma120 = float(s.ma120) if s.ma120 is not None else None
    ma200 = float(s.ma200) if s.ma200 is not None else None

    # 1. 돌파 감지 로직
    monitor_cross_signal(s, df_live, market, token, chat_id, cache_path)
    
    # 2. 정기 리포트 전송 여부 확인
    p120_txt, p200_txt = get_positions(cache_path, live_price, ma120, ma200)
    maybe_send_regular_report(s, df_live, market, token, chat_id, report_state_path, p120_txt, p200_txt)

    # 3. 스냅샷 저장
    save_snapshot(s)

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
