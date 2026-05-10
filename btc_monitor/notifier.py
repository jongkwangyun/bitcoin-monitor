import os
import logging
from typing import Optional
import requests

logger = logging.getLogger(__name__)

def send_telegram_photo(
    photo_png: bytes,
    caption: str = "",
    *,
    token: Optional[str] = None,
    chat_id: Optional[str] = None,
    parse_mode: Optional[str] = "HTML",
) -> None:
    token = (token or os.environ.get("TELEGRAM_BOT_TOKEN", "")).strip()
    chat_id = (chat_id or os.environ.get("TELEGRAM_CHAT_ID", "")).strip()
    if not token or not chat_id:
        logger.error("TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID 가 없습니다.")
        return

    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    data = {"chat_id": chat_id}
    if caption:
        data["caption"] = caption[:1024]
    if parse_mode:
        data["parse_mode"] = parse_mode
    files = {"photo": ("ma_chart.png", photo_png, "image/png")}
    
    try:
        r = requests.post(url, data=data, files=files, timeout=60)
        r.raise_for_status()
    except Exception as e:
        logger.exception(f"텔레그램 사진 전송 실패: {e}")

def send_telegram_html(text: str, token: Optional[str] = None, chat_id: Optional[str] = None) -> None:
    token = (token or os.environ.get("TELEGRAM_BOT_TOKEN", "")).strip()
    chat_id = (chat_id or os.environ.get("TELEGRAM_CHAT_ID", "")).strip()
    if not token or not chat_id:
        logger.error("TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID 가 없습니다.")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        r = requests.post(
            url,
            json={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
            },
            timeout=30,
        )
        r.raise_for_status()
    except Exception as e:
        logger.exception(f"텔레그램 메시지 전송 실패: {e}")
