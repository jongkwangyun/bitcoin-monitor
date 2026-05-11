import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from btc_monitor.report import format_my_position, format_snapshot_html

def load_report_state(path: str) -> dict:
    if not os.path.isfile(path):
        return {"last_report": ""}
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return data
    except (json.JSONDecodeError, OSError):
        return {"last_report": ""}

def save_report_state(path: str, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def should_send_regular_report(state_path: str) -> bool:
    now_kst = datetime.now(ZoneInfo("Asia/Seoul"))
    # 08시 또는 20시 (GitHub Actions 지연으로 08:01 등에 실행될 수 있으므로 hour만 체크)
    if now_kst.hour in (8, 20):
        report_id = now_kst.strftime("%Y-%m-%d-%H")
        state = load_report_state(state_path)
        if state.get("last_report") != report_id:
            state["last_report"] = report_id
            save_report_state(state_path, state)
            return True
    return False

def format_regular_report(s) -> str:
    base_text = format_snapshot_html(s)
    return f"<b>📊 BTC 정기 리포트</b>\n\n{base_text}"
