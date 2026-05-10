"""
Streamlit 대시보드: SQLite 스냅샷 시각화.

실행: streamlit run dashboard.py
"""

from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

_ROOT = Path(__file__).resolve().parent
load_dotenv(_ROOT / ".env")

from btc_monitor.persistence import load_recent_sqlite, sqlite_path

st.set_page_config(page_title="BTC 모니터", layout="wide")
st.title("BTC 모니터 대시보드")

limit = st.slider("표시 스냅샷 수", min_value=50, max_value=2000, value=500, step=50)
path = sqlite_path()
st.caption(f"SQLite: `{path}` (존재: {path.is_file()})")

rows = load_recent_sqlite(limit=limit)
if not rows:
    st.info("저장된 스냅샷이 없습니다. `daily_job.py` 또는 GitHub Actions를 먼저 실행하세요.")
    st.stop()

df = pd.DataFrame(rows)
df["ts_utc"] = pd.to_datetime(df["ts_utc"], utc=True)

c1, c2, c3 = st.columns(3)
last = df.iloc[-1]
c1.metric("최근 실시간가 (원)", f"{last['live_price_krw']:,.0f}")
if pd.notna(last.get("rsi14")):
    c2.metric("RSI(14)", f"{float(last['rsi14']):.1f}")
else:
    c2.metric("RSI(14)", "N/A")
if last.get("fear_greed") is not None:
    c3.metric("Fear & Greed", str(int(last["fear_greed"])))
else:
    c3.metric("Fear & Greed", "N/A")

st.subheader("가격")
chart_df = df.set_index("ts_utc")[["live_price_krw"]]
st.line_chart(chart_df)

st.subheader("RSI / 김프 / 주간 수익률")
aux = df.set_index("ts_utc")[
    [c for c in ["rsi14", "kimchi_pct", "weekly_return_pct"] if c in df.columns]
]
num_aux = aux.apply(pd.to_numeric, errors="coerce")
st.line_chart(num_aux)

st.subheader("스냅샷 테이블")
show_cols = [
    "ts_utc",
    "live_price_krw",
    "ma20",
    "ma120",
    "rsi14",
    "fear_greed",
    "btc_dominance_pct",
    "kimchi_pct",
    "volume_spike_ratio",
    "cross_status",
]
show_cols = [c for c in show_cols if c in df.columns]
st.dataframe(df[show_cols].sort_values("ts_utc", ascending=False), use_container_width=True)
