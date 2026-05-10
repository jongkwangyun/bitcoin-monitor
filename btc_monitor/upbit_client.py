from typing import Any, Dict, List, Optional, Union

import pandas as pd
import requests

from .config import CANDLE_COUNT, DEFAULT_MARKET

UPBIT_DAYS_URL = "https://api.upbit.com/v1/candles/days"
UPBIT_TICKER_URL = "https://api.upbit.com/v1/ticker"


def fetch_daily_candles(market: str = DEFAULT_MARKET, count: int = CANDLE_COUNT) -> pd.DataFrame:
    r = requests.get(UPBIT_DAYS_URL, params={"market": market, "count": count}, timeout=30)
    r.raise_for_status()
    rows = r.json()
    if not rows:
        raise RuntimeError("업비트에서 캔들 데이터가 비어 있습니다.")

    df = pd.DataFrame(rows)
    time_col = "candle_date_time_kst" if "candle_date_time_kst" in df.columns else "candle_date_time_utc"
    df = df.sort_values(time_col, ascending=True).reset_index(drop=True)
    df["trade_price"] = pd.to_numeric(df["trade_price"], errors="coerce")
    df["candle_acc_trade_volume"] = pd.to_numeric(df.get("candle_acc_trade_volume"), errors="coerce")
    if df["trade_price"].isna().any():
        raise RuntimeError("종가(trade_price) 파싱 실패")
    return df


def fetch_ticker(markets: Union[str, List[str]]) -> List[Dict[str, Any]]:
    if isinstance(markets, list):
        markets = ",".join(markets)
    r = requests.get(UPBIT_TICKER_URL, params={"markets": markets}, timeout=30)
    r.raise_for_status()
    data = r.json()
    if not data:
        raise RuntimeError("업비트 ticker 응답이 비어 있습니다.")
    return data


def fetch_krw_per_usdt() -> Optional[float]:
    """1 USDT당 원화(KRW-USDT 체결가). USD 환산에 사용."""
    try:
        tick = fetch_ticker("KRW-USDT")[0]
        v = float(tick["trade_price"])
        return v if v > 0 else None
    except (requests.RequestException, KeyError, ValueError, TypeError, IndexError):
        return None


def current_price_krw_btc(market: str = DEFAULT_MARKET) -> float:
    tick = fetch_ticker(market)[0]
    return float(tick["trade_price"])


def volume_24h_krw(market: str = DEFAULT_MARKET) -> float:
    tick = fetch_ticker(market)[0]
    return float(tick["acc_trade_volume_24h"])
