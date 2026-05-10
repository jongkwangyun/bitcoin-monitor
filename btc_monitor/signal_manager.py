import json
import os
from typing import Tuple

def load_alert_cache(path: str) -> dict:
    if not os.path.isfile(path):
        return {"ma_state": {}}
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data.get("ma_state"), dict):
            data["ma_state"] = {}
        return data
    except (json.JSONDecodeError, OSError):
        return {"ma_state": {}}

def save_alert_cache(path: str, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_current_position(live_price: float, ma_val: float) -> str:
    if ma_val is None:
        return "N/A"
    return "ABOVE" if live_price > ma_val else "BELOW"

def check_ma_cross(cache: dict, ma_label: str, ma_val: float, live_price: float) -> str:
    """
    MA 돌파 상태를 확인하고, 2회 이상 같은 방향 유지 시 알림 메시지 문자열을 반환합니다.
    """
    if ma_val is None:
        return ""
        
    current_pos = get_current_position(live_price, ma_val)
    
    state_key = f"state_{ma_label}"
    pending_key = f"pending_{ma_label}"
    count_key = f"count_{ma_label}"
    
    saved_state = cache["ma_state"].get(state_key)
    pending_state = cache["ma_state"].get(pending_key)
    pending_count = cache["ma_state"].get(count_key, 0)
    
    # 초기 설정
    if saved_state is None:
        cache["ma_state"][state_key] = current_pos
        cache["ma_state"][pending_key] = None
        cache["ma_state"][count_key] = 0
        return ""
        
    # 기존 상태 유지 중
    if current_pos == saved_state:
        if pending_state is not None or pending_count > 0:
            cache["ma_state"][pending_key] = None
            cache["ma_state"][count_key] = 0
        return ""
        
    # 상태 변경 발생 (돌파 시도)
    if current_pos == pending_state:
        pending_count += 1
        cache["ma_state"][count_key] = pending_count
        
        # 30분 간격으로 2회 연속 같은 방향 유지 -> 1시간 후 확정 (pending_count == 2일 때 알림)
        if pending_count == 2:
            direction = "상향 돌파" if current_pos == "ABOVE" else "하향 이탈"
            alert_msg = f"🚨 BTC {ma_label}일선 {direction} 확정"
            
            # 상태 확정 업데이트
            cache["ma_state"][state_key] = current_pos
            cache["ma_state"][pending_key] = None
            cache["ma_state"][count_key] = 0
            return alert_msg
    else:
        # 새로운 방향으로 첫 이탈/돌파 발생
        cache["ma_state"][pending_key] = current_pos
        cache["ma_state"][count_key] = 1
        
    return ""

def get_positions(cache_path: str, live_price: float, ma120: float, ma200: float) -> Tuple[str, str]:
    # 현재 위치 문자열을 한글로 반환 (리포트용)
    pos_120 = get_current_position(live_price, ma120)
    pos_200 = get_current_position(live_price, ma200)
    p120_txt = "위" if pos_120 == "ABOVE" else "아래" if pos_120 == "BELOW" else "N/A"
    p200_txt = "위" if pos_200 == "ABOVE" else "아래" if pos_200 == "BELOW" else "N/A"
    return p120_txt, p200_txt
