from typing import Optional

import pandas as pd


def add_moving_averages(df: pd.DataFrame, close_col: str = "trade_price") -> pd.DataFrame:
    out = df.copy()
    close = out[close_col]
    out["ma5"] = close.rolling(5).mean()
    out["ma20"] = close.rolling(20).mean()
    out["ma60"] = close.rolling(60).mean()
    out["ma120"] = close.rolling(120).mean()
    out["ma200"] = close.rolling(200).mean()
    return out


def rsi_wilder(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0.0)
    loss = (-delta).clip(lower=0.0)
    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, float("nan"))
    out = 100.0 - (100.0 / (1.0 + rs))
    return out


def apply_live_price(df: pd.DataFrame, live_price: float, close_col: str = "trade_price") -> pd.DataFrame:
    """최신 일봉 종가를 실시간 시세로 치환해 당일 구간 기준 지표를 맞춘다."""
    out = df.copy()
    if len(out) < 1:
        return out
    out.loc[out.index[-1], close_col] = live_price
    return out


def weekly_return_pct(df: pd.DataFrame, live_price: float, close_col: str = "trade_price") -> Optional[float]:
    """최근 7거래일 전 종가 대비 실시간 수익률."""
    if len(df) < 8:
        return None
    prev = float(df.iloc[-8][close_col])
    if prev == 0:
        return None
    return (live_price / prev - 1.0) * 100.0


def volume_spike_ratio(daily_volumes: pd.Series, vol_24h: float, lookback: int = 20) -> Optional[float]:
    """24시간 거래대금(원) / 최근 일봉 일별 거래대금 평균."""
    if daily_volumes.isna().all() or lookback < 1:
        return None
    tail = daily_volumes.dropna().iloc[-lookback:]
    if len(tail) < 1:
        return None
    avg = float(tail.mean())
    if avg == 0:
        return None
    return vol_24h / avg
