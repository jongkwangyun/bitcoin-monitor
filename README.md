# Bitcoin Monitor

Bitcoin Monitor는 업비트 KRW-BTC 가격을 모니터링하고 Telegram으로 알림을 전송하는 Python 프로젝트입니다. 이 프로젝트는 같은 workspace의 `common` 패키지를 editable install로 사용합니다.

## 구조

```text
bitcoin-monitor/
├── btc_monitor/
│   ├── __init__.py
│   ├── bot.py
│   ├── monitor.py
│   └── ...
├── requirements.txt
└── README.md
```

## 설치

가상환경은 PC마다 새로 만들어야 합니다. 다른 PC나 다른 경로에서 만든 `.venv`를 복사해서 사용하면 `pip.exe`가 이전 Python 경로를 참조해 실행 오류가 발생할 수 있습니다.

```powershell
Set-Location C:\1work\bitcoin-monitor
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

`requirements.txt`에는 `common` editable install이 포함되어 있습니다.

```text
-e ../common
```

## 기존 `.venv` 오류 해결

아래처럼 `D:\Cursor\...` 또는 이전 PC의 경로를 참조하는 오류가 나오면 `.venv`를 삭제하고 다시 생성합니다.

```text
Fatal error in launcher: Unable to create process using ...
```

```powershell
Set-Location C:\1work\bitcoin-monitor
deactivate
Remove-Item -Recurse -Force .venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 설정

`.env` 파일에 Telegram 설정을 입력합니다.

```env
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
ALLOWED_CHAT_IDS=your_chat_id
UPBIT_MARKET=KRW-BTC
```

## 실행

모니터 실행:

```powershell
Set-Location C:\1work\bitcoin-monitor
python -m btc_monitor.monitor
```

Telegram 명령 bot 실행:

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
