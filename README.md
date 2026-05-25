# Bitcoin Monitor

Bitcoin Monitor? ??? KRW-BTC ??? ?????? Telegram ??? ??? ?? ???? Python ???????. ? ????? workspace monorepo? `common` ???? editable install? ?????.

## ??

```text
bitcoin-monitor/
 btc_monitor/
    __init__.py
    bot.py
    monitor.py
    ...
 requirements.txt
 README.md
```

## ??

```powershell
Set-Location C:\1work\bitcoin-monitor
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

`requirements.txt`?? ?? ??? ??? ?????.

```powershell
pip install -e ../common
```

## ??

`.env` ??? Telegram ??? ?????.

```env
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
ALLOWED_CHAT_IDS=your_chat_id
UPBIT_MARKET=KRW-BTC
```

## ??

??/?? ??? ??:

```powershell
Set-Location C:\1work\bitcoin-monitor
python -m btc_monitor.monitor
```

Telegram ??? ? ??:

```powershell
Set-Location C:\1work\bitcoin-monitor
python -m btc_monitor.bot
```

Root-level `bot.py`, `monitor.py`, and `daily_job.py` are compatibility wrappers. New execution should use `python -m btc_monitor.monitor` and `python -m btc_monitor.bot`.

## Import rules

Use the editable-installed `common` package with absolute imports.

```python
from common.telegram import send_telegram_html
from common.http_session import get_session
```

Do not rely on `sys.path` changes or manual `PYTHONPATH` settings.
