import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from btc_monitor.report import format_my_position

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

def format_regular_report(s, p120_txt: str, p200_txt: str) -> str:
    lines = []
    lines.append("<b>📊 BTC 정기 리포트</b>\n")
    
    krw_txt = f"₩{s.live_price_krw:,.0f}"
    if s.krw_per_usdt:
        usd = s.live_price_krw / s.krw_per_usdt
        krw_txt = f"${usd:,.2f} ({krw_txt})"
    lines.append(f"• 현재가: <b>{krw_txt}</b>\n")
    
    pos_str = format_my_position(s.live_price_krw)
    if pos_str:
        lines.append(pos_str)
    
    def ma_txt(val):
        if val is None: return "N/A"
        if s.krw_per_usdt:
            return f"${val/s.krw_per_usdt:,.0f}"
        return f"₩{val:,.0f}"
        
    lines.append(f"• 5MA: {ma_txt(s.ma5)}")
    lines.append(f"• 20MA: {ma_txt(s.ma20)}")
    lines.append(f"• 60MA: {ma_txt(s.ma60)}")
    lines.append(f"• 120MA: {ma_txt(s.ma120)}")
    lines.append(f"• 200MA: {ma_txt(s.ma200)}")
    lines.append("")
    
    lines.append(f"• RSI(14): {s.rsi14:.2f}" if s.rsi14 else "• RSI(14): N/A")
    lines.append(f"• Fear & Greed: {s.fear_greed} ({s.fear_greed_label})" if s.fear_greed is not None else "• Fear & Greed: N/A")
    lines.append(f"• BTC Dominance: {s.btc_dominance_pct:.2f}%" if s.btc_dominance_pct is not None else "• BTC Dominance: N/A")
    lines.append(f"• 김프: {s.kimchi_pct:+.3f}%" if s.kimchi_pct is not None else "• 김프: N/A")
    lines.append(f"• 주간 수익률: {s.weekly_return_pct:+.2f}%" if s.weekly_return_pct is not None else "• 주간 수익률: N/A")
    lines.append("")
    
    lines.append("<b>• 현재 상태</b>")
    lines.append(f"  - 120MA: {p120_txt}")
    lines.append(f"  - 200MA: {p200_txt}")
    
    return "\n".join(lines)
