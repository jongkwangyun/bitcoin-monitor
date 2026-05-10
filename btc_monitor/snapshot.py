from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from .config import CANDLE_COUNT, DEFAULT_MARKET
from .external_apis import (
    alt_season_label,
    fetch_coingecko_global,
    fetch_fear_greed_index,
)
from .indicators import (
    add_moving_averages,
    apply_live_price,
    rsi_wilder,
    volume_spike_ratio,
    weekly_return_pct,
)
from .kimchi import kimchi_premium_pct
from .upbit_client import (
    current_price_krw_btc,
    fetch_daily_candles,
    fetch_krw_per_usdt,
    volume_24h_krw,
)


@dataclass
class CrossEvent:
    label: str
    direction: str  # 상향_돌파 / 하향_이탈


@dataclass
class MarketSnapshot:
    market: str
    candle_date_label: str
    live_price_krw: float
    ma5: Optional[float]
    ma20: Optional[float]
    ma60: Optional[float]
    ma120: Optional[float]
    ma200: Optional[float]
    rsi14: Optional[float]
    fear_greed: Optional[int]
    fear_greed_label: str
    btc_dominance_pct: Optional[float]
    alt_season_text: str
    kimchi_pct: Optional[float]
    weekly_return_pct: Optional[float]
    volume_spike_ratio: Optional[float]
    krw_per_usdt: Optional[float] = None
    crosses: List[CrossEvent] = field(default_factory=list)


def compare_price_to_ma(price: float, ma: Optional[float]) -> str:
    if ma is None or pd.isna(ma):
        return "N/A"
    if price > float(ma):
        return "위"
    if price < float(ma):
        return "아래"
    return "일치"


def pct_vs_ma(price: float, ma: Optional[float]) -> str:
    if ma is None or pd.isna(ma) or float(ma) == 0:
        return "N/A"
    pct = (price / float(ma) - 1.0) * 100.0
    return f"{pct:+.2f}%"


def detect_ma_crosses(prev_row: pd.Series, curr_row: pd.Series) -> List[CrossEvent]:
    events: List[CrossEvent] = []
    pairs = [("ma120", "120일선"), ("ma200", "200일선")]
    for col, label in pairs:
        p0, p1 = float(prev_row["trade_price"]), float(curr_row["trade_price"])
        m0, m1 = prev_row[col], curr_row[col]
        if pd.isna(m0) or pd.isna(m1):
            continue
        m0, m1 = float(m0), float(m1)
        if p0 < m0 and p1 > m1:
            events.append(CrossEvent(label=label, direction="상향_돌파"))
        elif p0 > m0 and p1 < m1:
            events.append(CrossEvent(label=label, direction="하향_이탈"))
    return events


def cross_signature_from_snapshot(s: MarketSnapshot, ev: CrossEvent) -> str:
    return f"{s.candle_date_label}|{ev.label}|{ev.direction}"


def cross_status_text(crosses: List[CrossEvent]) -> str:
    if not crosses:
        return "당일 돌파 신호 없음 (120·200일선 기준, 실시간가)"
    parts = []
    for ev in crosses:
        if ev.direction == "상향_돌파":
            parts.append(f"{ev.label} 상향 돌파")
        else:
            parts.append(f"{ev.label} 하향 이탈")
    return " / ".join(parts)


def build_snapshot_full(
    market: str = DEFAULT_MARKET,
) -> Tuple[MarketSnapshot, pd.Series, pd.Series, pd.DataFrame]:
    """스냅샷, 전일/금일 행, 실시간 반영 일봉 DataFrame(차트용)을 반환한다."""
    live = current_price_krw_btc(market)
    vol24 = volume_24h_krw(market)
    krw_usdt = fetch_krw_per_usdt()

    df = fetch_daily_candles(market=market, count=CANDLE_COUNT)
    if len(df) < 2:
        raise RuntimeError("캔들이 2개 미만입니다.")
    df_live = apply_live_price(df, live)
    df_live = add_moving_averages(df_live)
    rsi_series = rsi_wilder(df_live["trade_price"], 14)
    rsi_last = float(rsi_series.iloc[-1]) if len(rsi_series) and not pd.isna(rsi_series.iloc[-1]) else None

    daily_vol = df_live["candle_acc_trade_volume"] if "candle_acc_trade_volume" in df_live.columns else None
    vs_ratio = None
    if daily_vol is not None:
        vs_ratio = volume_spike_ratio(daily_vol.astype(float), vol24)

    wret = weekly_return_pct(df, live)

    fg = fetch_fear_greed_index()
    glob = fetch_coingecko_global()
    alt_txt = alt_season_label(glob.btc_dominance_pct)
    kimchi = kimchi_premium_pct()

    last = df_live.iloc[-1]
    prev = df_live.iloc[-2]
    crosses = detect_ma_crosses(prev, last)

    date_label = str(last.get("candle_date_time_kst", last.get("candle_date_time_utc", "")))

    snap = MarketSnapshot(
        market=market,
        candle_date_label=date_label,
        live_price_krw=live,
        ma5=_f(last.get("ma5")),
        ma20=_f(last.get("ma20")),
        ma60=_f(last.get("ma60")),
        ma120=_f(last.get("ma120")),
        ma200=_f(last.get("ma200")),
        rsi14=rsi_last,
        fear_greed=fg.value,
        fear_greed_label=fg.classification,
        btc_dominance_pct=glob.btc_dominance_pct,
        alt_season_text=alt_txt,
        kimchi_pct=kimchi,
        weekly_return_pct=wret,
        volume_spike_ratio=vs_ratio,
        krw_per_usdt=krw_usdt,
        crosses=crosses,
    )
    return snap, prev, last, df_live


def build_snapshot(market: str = DEFAULT_MARKET) -> MarketSnapshot:
    s, _, _, _ = build_snapshot_full(market)
    return s


def _f(x) -> Optional[float]:
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return None
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def snapshot_to_dict(s: MarketSnapshot) -> Dict[str, Any]:
    return {
        "market": s.market,
        "candle_date_label": s.candle_date_label,
        "live_price_krw": s.live_price_krw,
        "ma5": s.ma5,
        "ma20": s.ma20,
        "ma60": s.ma60,
        "ma120": s.ma120,
        "ma200": s.ma200,
        "rsi14": s.rsi14,
        "fear_greed": s.fear_greed,
        "fear_greed_label": s.fear_greed_label,
        "btc_dominance_pct": s.btc_dominance_pct,
        "alt_season_text": s.alt_season_text,
        "kimchi_pct": s.kimchi_pct,
        "weekly_return_pct": s.weekly_return_pct,
        "volume_spike_ratio": s.volume_spike_ratio,
        "cross_status": cross_status_text(s.crosses),
    }
