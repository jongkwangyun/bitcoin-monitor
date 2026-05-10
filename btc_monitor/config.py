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

MY_BTC_BUY_PRICE = float(os.environ.get("MY_BTC_BUY_PRICE", "113115239.0"))
MY_BTC_AMOUNT = float(os.environ.get("MY_BTC_AMOUNT", "0.13557626"))
