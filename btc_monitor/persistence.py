import csv
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import csv_path, sqlite_path
from .snapshot import MarketSnapshot, snapshot_to_dict


def _utc_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


SQL_CREATE = """
CREATE TABLE IF NOT EXISTS snapshots (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts_utc TEXT NOT NULL,
  market TEXT NOT NULL,
  live_price_krw REAL NOT NULL,
  ma5 REAL,
  ma20 REAL,
  ma60 REAL,
  ma120 REAL,
  ma200 REAL,
  rsi14 REAL,
  fear_greed INTEGER,
  btc_dominance_pct REAL,
  alt_season_text TEXT,
  kimchi_pct REAL,
  weekly_return_pct REAL,
  volume_spike_ratio REAL,
  cross_status TEXT
);
"""


def init_sqlite(path: Optional[Path] = None) -> None:
    p = path or sqlite_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(p) as conn:
        conn.execute(SQL_CREATE)
        conn.commit()


def save_snapshot(s: MarketSnapshot, path: Optional[Path] = None) -> None:
    init_sqlite(path)
    p = path or sqlite_path()
    row = snapshot_to_dict(s)
    ts = _utc_iso()
    with sqlite3.connect(p) as conn:
        conn.execute(
            """
            INSERT INTO snapshots (
              ts_utc, market, live_price_krw, ma5, ma20, ma60, ma120, ma200,
              rsi14, fear_greed, btc_dominance_pct, alt_season_text,
              kimchi_pct, weekly_return_pct, volume_spike_ratio, cross_status
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                ts,
                s.market,
                s.live_price_krw,
                s.ma5,
                s.ma20,
                s.ma60,
                s.ma120,
                s.ma200,
                s.rsi14,
                s.fear_greed,
                s.btc_dominance_pct,
                s.alt_season_text,
                s.kimchi_pct,
                s.weekly_return_pct,
                s.volume_spike_ratio,
                row["cross_status"],
            ),
        )
        conn.commit()

    append_csv(s, ts)


CSV_FIELDS = [
    "ts_utc",
    "market",
    "live_price_krw",
    "ma5",
    "ma20",
    "ma60",
    "ma120",
    "ma200",
    "rsi14",
    "fear_greed",
    "btc_dominance_pct",
    "alt_season_text",
    "kimchi_pct",
    "weekly_return_pct",
    "volume_spike_ratio",
    "cross_status",
]


def append_csv(s: MarketSnapshot, ts_utc: str, path: Optional[Path] = None) -> None:
    p = path or csv_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    row = snapshot_to_dict(s)
    flat: Dict[str, Any] = {
        "ts_utc": ts_utc,
        "market": s.market,
        "live_price_krw": s.live_price_krw,
        "ma5": s.ma5,
        "ma20": s.ma20,
        "ma60": s.ma60,
        "ma120": s.ma120,
        "ma200": s.ma200,
        "rsi14": s.rsi14,
        "fear_greed": s.fear_greed,
        "btc_dominance_pct": s.btc_dominance_pct,
        "alt_season_text": s.alt_season_text,
        "kimchi_pct": s.kimchi_pct,
        "weekly_return_pct": s.weekly_return_pct,
        "volume_spike_ratio": s.volume_spike_ratio,
        "cross_status": row["cross_status"],
    }
    write_header = not p.is_file()
    with p.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        if write_header:
            w.writeheader()
        w.writerow(flat)


def load_recent_sqlite(limit: int = 500, path: Optional[Path] = None) -> List[Dict[str, Any]]:
    p = path or sqlite_path()
    if not p.is_file():
        return []
    with sqlite3.connect(p) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(
            "SELECT * FROM snapshots ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        rows = cur.fetchall()
    return [dict(r) for r in reversed(rows)]
