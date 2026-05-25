"""Compatibility entrypoint for the BTC monitor package."""

from btc_monitor.monitor import main

if __name__ == "__main__":
    raise SystemExit(main())
