from html import escape
from typing import List, Optional

from .snapshot import CrossEvent, MarketSnapshot, compare_price_to_ma, cross_status_text, pct_vs_ma


def format_price_usd_krw(krw: float, krw_per_usdt: Optional[float]) -> str:
    """텔레그램용: USD 우선, 괄호에 원화 (환율 없으면 원화만)."""
    if krw_per_usdt and krw_per_usdt > 0:
        usd = krw / krw_per_usdt
        return f"${usd:,.2f} (₩{krw:,.0f})"
    return f"₩{krw:,.0f}"


def format_ma_line_usd_krw(
    live_krw: float,
    ma: Optional[float],
    krw_per_usdt: Optional[float],
) -> str:
    if ma is None:
        return "N/A"
    pos = compare_price_to_ma(live_krw, ma)
    pct = pct_vs_ma(live_krw, ma)
    price_txt = format_price_usd_krw(float(ma), krw_per_usdt)
    return f"{price_txt} — 현재가 <b>{pos}</b> ({pct})"


def format_snapshot_html(s: MarketSnapshot, fetched_at: Optional[str] = None) -> str:
    lines: List[str] = []
    lines.append(f"<b>[BTC] {escape(s.market)}</b>")
    lines.append(f"실시간가: <b>{format_price_usd_krw(s.live_price_krw, s.krw_per_usdt)}</b>")
    if fetched_at:
        lines.append(f"조회 시각: <b>{escape(fetched_at)}</b>")
    lines.append(f"일봉 기준일: {escape(str(s.candle_date_label))}")
    lines.append("")
    lines.append("<b>이동평균 (실시간가 대비)</b>")
    for name, col in [
        ("5일", s.ma5),
        ("20일", s.ma20),
        ("60일", s.ma60),
        ("120일", s.ma120),
        ("200일", s.ma200),
    ]:
        lines.append(f"· {name}: {format_ma_line_usd_krw(s.live_price_krw, col, s.krw_per_usdt)}")

    lines.append("")
    lines.append("<b>시장 지표</b>")
    if s.fear_greed is not None:
        lines.append(f"· Fear &amp; Greed: {s.fear_greed} ({escape(s.fear_greed_label)})")
    else:
        lines.append("· Fear &amp; Greed: N/A")
    if s.btc_dominance_pct is not None:
        lines.append(f"· BTC 도미넌스: {s.btc_dominance_pct:.2f}%")
    else:
        lines.append("· BTC 도미넌스: N/A")
    lines.append(f"· 알트 시즌 지표: {escape(s.alt_season_text)}")

    lines.append("")
    lines.append("<b>기술·국내</b>")
    if s.rsi14 is not None:
        lines.append(f"· RSI(14): {s.rsi14:.2f}")
    else:
        lines.append("· RSI(14): N/A")
    if s.volume_spike_ratio is not None:
        lines.append(f"· 거래량 급증 지표: 24h / 20일평균일거래 ≒ <b>{s.volume_spike_ratio:.2f}x</b>")
    else:
        lines.append("· 거래량 급증 지표: N/A")
    if s.kimchi_pct is not None:
        lines.append(f"· 업비트 김프: <b>{s.kimchi_pct:+.3f}%</b>")
    else:
        lines.append("· 업비트 김프: N/A")
    if s.weekly_return_pct is not None:
        lines.append(f"· 주간 수익률(약 7거래일): <b>{s.weekly_return_pct:+.2f}%</b>")
    else:
        lines.append("· 주간 수익률: N/A")

    lines.append("")
    lines.append(f"<b>120/200일선 돌파</b>: {escape(cross_status_text(s.crosses))}")

    return "\n".join(lines)


def format_cross_alert(s: MarketSnapshot, ev: CrossEvent, prev_price: float, curr_price: float) -> str:
    if ev.direction == "상향_돌파":
        verb = f"{ev.label} 상향 돌파"
    else:
        verb = f"{ev.label} 하향 이탈"
    prev_txt = format_price_usd_krw(prev_price, s.krw_per_usdt)
    curr_txt = format_price_usd_krw(curr_price, s.krw_per_usdt)
    return (
        f"<b>⚠️ BTC 경고 ({escape(s.market)})</b>\n"
        f"{verb}\n"
        f"전일 종가: {prev_txt} → 실시간: {curr_txt}"
    )
