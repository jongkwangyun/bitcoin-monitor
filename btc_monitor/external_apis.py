from dataclasses import dataclass
from typing import Any, Dict, Optional

from .http_session import get_session

_session = get_session()


@dataclass
class FearGreedResult:
    value: Optional[int]
    classification: str


def fetch_fear_greed_index() -> FearGreedResult:
    """Alternative.me Fear & Greed Index."""
    try:
        r = _session.get("https://api.alternative.me/fng/", params={"limit": 1}, timeout=20)
        r.raise_for_status()
        data = r.json().get("data") or []
        if not data:
            return FearGreedResult(value=None, classification="N/A")
        row = data[0]
        return FearGreedResult(
            value=int(row["value"]),
            classification=str(row.get("value_classification", "")),
        )
    except (KeyError, ValueError, OSError):
        return FearGreedResult(value=None, classification="조회 실패")


@dataclass
class GlobalMarketResult:
    btc_dominance_pct: Optional[float]
    market_cap_change_24h_pct: Optional[float]
    raw: Dict[str, Any]


def fetch_coingecko_global() -> GlobalMarketResult:
    """글로벌 시총 및 BTC 도미넌스."""
    try:
        r = _session.get("https://api.coingecko.com/api/v3/global", timeout=20)
        r.raise_for_status()
        g = r.json().get("data") or {}
        dom = g.get("market_cap_percentage") or {}
        btc_dom = dom.get("btc")
        ch = g.get("market_cap_change_percentage_24h_usd")
        return GlobalMarketResult(
            btc_dominance_pct=float(btc_dom) if btc_dom is not None else None,
            market_cap_change_24h_pct=float(ch) if ch is not None else None,
            raw=g,
        )
    except (TypeError, ValueError, OSError):
        return GlobalMarketResult(btc_dominance_pct=None, market_cap_change_24h_pct=None, raw={})


def alt_season_label(btc_dominance_pct: Optional[float]) -> str:
    """도미넌스 기반 알트 시즌 성향 (Blockchain Center 지수 대체 설명)."""
    if btc_dominance_pct is None:
        return "N/A"
    d = btc_dominance_pct
    if d < 42:
        return "알트 시즌 성향 (도미넌스 낮음)"
    if d < 52:
        return "중립 구간"
    return "BTC 우위 구간"
