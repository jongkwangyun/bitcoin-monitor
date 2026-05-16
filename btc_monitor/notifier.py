import logging
import time
from typing import Optional

from .http_session import get_session

logger = logging.getLogger(__name__)

_session = get_session()

_MAX_RETRIES = 3
_BACKOFF_BASE = 2  # seconds: 2 → 4 → 8


def _send_with_retry(method: str, url: str, **kwargs) -> None:
    """Telegram API 호출을 최대 _MAX_RETRIES회 재시도한다 (지수 백오프)."""
    last_exc: Optional[Exception] = None
    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            r = _session.request(method, url, **kwargs)
            r.raise_for_status()
            return
        except Exception as e:
            last_exc = e
            if attempt < _MAX_RETRIES:
                wait = _BACKOFF_BASE ** attempt
                logger.warning(
                    "Telegram 전송 실패 (시도 %d/%d), %ds 후 재시도: %s",
                    attempt, _MAX_RETRIES, wait, e,
                )
                time.sleep(wait)
    logger.error("Telegram 전송 최종 실패 (%d회 시도): %s", _MAX_RETRIES, last_exc)


def send_telegram_photo(
    photo_png: bytes,
    caption: str = "",
    *,
    token: Optional[str] = None,
    chat_id: Optional[str] = None,
    parse_mode: Optional[str] = "HTML",
) -> None:
    import os
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

    _send_with_retry("POST", url, data=data, files=files, timeout=60)


def send_telegram_html(text: str, token: Optional[str] = None, chat_id: Optional[str] = None) -> None:
    import os
    token = (token or os.environ.get("TELEGRAM_BOT_TOKEN", "")).strip()
    chat_id = (chat_id or os.environ.get("TELEGRAM_CHAT_ID", "")).strip()
    if not token or not chat_id:
        logger.error("TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID 가 없습니다.")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    _send_with_retry(
        "POST",
        url,
        json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        },
        timeout=30,
    )
