"""
텔레그램 봇 (업비트 BTC 조회). Render 등에서 24시간 폴링 실행.

환경변수: TELEGRAM_BOT_TOKEN (필수)
선택: ALLOWED_CHAT_IDS — 쉼표로 구분해 허용 채팅만 처리 (비우면 전체 허용)
"""

import io
import logging
import os
from datetime import datetime
from html import escape
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from telegram import InputFile, Update
from telegram.ext import Application, CommandHandler, ContextTypes

_ROOT = Path(__file__).resolve().parent
load_dotenv(_ROOT / ".env")

from btc_monitor.ma_chart import render_ma_chart_png
from btc_monitor.report import format_snapshot_html
from btc_monitor.snapshot import build_snapshot_full

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    level=logging.INFO,
)
LOG = logging.getLogger("btc_bot")


def allowed_chat(update: Update) -> bool:
    raw = os.environ.get("ALLOWED_CHAT_IDS", "").strip()
    if not raw:
        return True
    cid = update.effective_chat.id if update.effective_chat else None
    if cid is None:
        return False
    allowed = {int(x.strip()) for x in raw.split(",") if x.strip().isdigit()}
    return cid in allowed


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not allowed_chat(update):
        return
    await update.message.reply_html(
        "<b>BTC 모니터 봇</b>\n"
        "/btc — 업비트 KRW-BTC 실시간가, 이동평균, 지표, 120·200일선 돌파 여부",
    )


async def cmd_btc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not allowed_chat(update):
        await update.message.reply_text("허용되지 않은 채팅입니다.")
        return
    market = os.environ.get("UPBIT_MARKET", "KRW-BTC").strip() or "KRW-BTC"
    await update.message.reply_chat_action(action="typing")
    try:
        snap, _prev, _last, df_live = build_snapshot_full(market=market)
        fetched_at = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S")
        text = format_snapshot_html(snap, fetched_at=fetched_at)
        # Telegram 메시지 길이 제한 대비 분할
        if len(text) > 3500:
            text = text[:3500] + "\n…(생략)"
        await update.message.reply_html(text)
    except Exception as e:
        LOG.exception("btc failed")
        await update.message.reply_text(f"조회 실패: {e}")
        return

    try:
        chart_png = render_ma_chart_png(df_live, market)
        cap = (
            "<b>이동평균 차트</b>\n"
            f"{escape(market)} · 일봉 종가(최종 봉에 실시간가 반영)\n"
            f"조회 시각: {escape(fetched_at)}"
        )
        await update.message.reply_photo(
            photo=InputFile(io.BytesIO(chart_png), filename="ma_chart.png"),
            caption=cap[:1024],
            parse_mode="HTML",
        )
    except Exception as e:
        LOG.exception("btc chart failed")
        await update.message.reply_text(f"차트 전송 실패: {e}")


def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        raise SystemExit("TELEGRAM_BOT_TOKEN 이 필요합니다.")

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("btc", cmd_btc))

    LOG.info("Starting polling…")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
