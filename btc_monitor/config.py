import os
from pathlib import Path

_ENV_DIR = Path(__file__).resolve().parent.parent


def data_dir() -> Path:
    p = Path(os.environ.get("BTC_DATA_DIR", str(_ENV_DIR / "data"))).resolve()
    p.mkdir(parents=True, exist_ok=True)
    return p


def sqlite_path() -> Path:
    return data_dir() / os.environ.get("BTC_SQLITE_NAME", "monitor.db")


def csv_path() -> Path:
    return data_dir() / os.environ.get("BTC_CSV_NAME", "btc_snapshots.csv")


DEFAULT_MARKET = "KRW-BTC"
CANDLE_COUNT = 200
