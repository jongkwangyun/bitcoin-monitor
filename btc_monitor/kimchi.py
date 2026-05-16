from typing import Optional

from .http_session import get_session
from .upbit_client import fetch_ticker

_session = get_session()


def kimchi_premium_pct() -> Optional[float]:
    """
    김치 프리미엄 ≈ (업비트 KRW-BTC) / (바이낸스 BTCUSDT × 업비트 USDT 가격) - 1
    """
    try:
        up = fetch_ticker(["KRW-BTC", "KRW-USDT"])
        by_market = {x["market"]: x for x in up}
        krw_btc = float(by_market["KRW-BTC"]["trade_price"])
        krw_usdt = float(by_market["KRW-USDT"]["trade_price"])
        r = _session.get(
            "https://api.binance.com/api/v3/ticker/price",
            params={"symbol": "BTCUSDT"},
            timeout=20,
        )
        r.raise_for_status()
        usdt_btc = float(r.json()["price"])
        implied_krw = usdt_btc * krw_usdt
        if implied_krw <= 0:
            return None
        return (krw_btc / implied_krw - 1.0) * 100.0
    except (KeyError, ValueError, TypeError, OSError):
        return None
