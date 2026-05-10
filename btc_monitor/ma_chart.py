"""일봉 + 실시간가 기준 이동평균선 차트 (PNG 바이트)."""

from __future__ import annotations

import io

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd


def render_ma_chart_png(df_live: pd.DataFrame, market: str) -> bytes:
    """
    trade_price 및 MA(5~200) 시계열을 선 그래프로 그린 PNG 바이트열.
    """
    if df_live is None or len(df_live) < 2:
        raise ValueError("차트용 캔들 데이터가 부족합니다.")

    time_col = "candle_date_time_kst" if "candle_date_time_kst" in df_live.columns else "candle_date_time_utc"
    t = pd.to_datetime(df_live[time_col])
    price = pd.to_numeric(df_live["trade_price"], errors="coerce")

    fig, ax = plt.subplots(figsize=(11, 5.5), dpi=120)
    ax.plot(t, price, color="#1f77b4", linewidth=1.8, label="Close (live on last bar)")

    ma_specs = [
        ("ma5", "#ff7f0e", "MA5"),
        ("ma20", "#2ca02c", "MA20"),
        ("ma60", "#d62728", "MA60"),
        ("ma120", "#9467bd", "MA120"),
        ("ma200", "#8c564b", "MA200"),
    ]
    for col, color, lab in ma_specs:
        if col not in df_live.columns:
            continue
        s = pd.to_numeric(df_live[col], errors="coerce")
        if s.notna().any():
            ax.plot(t, s, color=color, linewidth=1.1, alpha=0.9, label=lab)

    ax.set_title(f"{market} — daily + moving averages")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price (KRW)")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    fig.autofmt_xdate(rotation=30)
    ax.grid(True, alpha=0.25)
    ax.legend(loc="upper left", fontsize=8, ncol=2)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:,.0f}"))

    buf = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf.read()
