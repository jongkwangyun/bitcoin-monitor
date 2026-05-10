import os
from typing import Optional

import requests


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
        raise RuntimeError("TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID 가 없습니다.")

    url = "https://api.telegram.org/bot{0}/sendPhoto".format(token)
    data = {"chat_id": chat_id}
    if caption:
        data["caption"] = caption[:1024]
    if parse_mode:
        data["parse_mode"] = parse_mode
    files = {"photo": ("ma_chart.png", photo_png, "image/png")}
    r = requests.post(url, data=data, files=files, timeout=60)
    if not r.ok:
        raise RuntimeError("텔레그램 사진 전송 실패 HTTP {0}: {1}".format(r.status_code, r.text))


def send_telegram_html(text: str, token: Optional[str] = None, chat_id: Optional[str] = None) -> None:
    token = (token or os.environ.get("TELEGRAM_BOT_TOKEN", "")).strip()
    chat_id = (chat_id or os.environ.get("TELEGRAM_CHAT_ID", "")).strip()
    if not token or not chat_id:
        raise RuntimeError("TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID 가 없습니다.")

    url = "https://api.telegram.org/bot{0}/sendMessage".format(token)
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
    if not r.ok:
        raise RuntimeError("텔레그램 전송 실패 HTTP {0}: {1}".format(r.status_code, r.text))
