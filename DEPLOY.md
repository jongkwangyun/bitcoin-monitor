# 배포 가이드

## Python 버전

이 프로젝트는 **Python 3.8 이상**을 가정합니다 (권장: **3.10 또는 3.11**).  
`python --version` 으로 확인하고, 구버전이면 [python.org](https://www.python.org/downloads/) 또는 Windows용 **Microsoft Store**에서 새 버전을 설치한 뒤 `py -3.11` 처럼 실행하거나 PATH에서 새 `python`을 쓰세요.

## 전제

- **텔레그램 봇 토큰**: @BotFather 에서 발급
- **채팅 ID**: 예약 알림(`daily_job`)용 `TELEGRAM_CHAT_ID` — GitHub Secrets 및 로컬 `.env`에 설정

## Windows: Python 3.11 가상환경 (권장)

시스템 기본 `python`이 3.6이어도, **py 런처**로 3.11 가상환경을 쓰면 됩니다.

1. 프로젝트 폴더에서 **`setup_venv.bat`** 더블클릭 또는 CMD에서 실행  
   → `py -3.11 -m venv .venv` 후 `requirements.txt` 설치
2. 이후 실행은 **`run_daily_job.bat`**, **`run_bot.bat`**, **`run_dashboard.bat`** 를 사용하거나,
3. 터미널에서 활성화 후 실행:
   ```bat
   .venv\Scripts\activate.bat
   python daily_job.py
   ```

Cursor/VS Code에서 이 폴더를 워크스페이스 루트로 열면 `.vscode/settings.json` 이 **`.venv`의 Python 3.11** 을 가리킵니다.

## 로컬 실행

```bash
cd bitcoin-monitor
pip install -r requirements.txt
# .env 에 TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID 설정

python daily_job.py          # 스냅샷 + CSV/SQLite + 텔레그램 요약
python bot.py                # /btc 명령 처리 (폴링)
streamlit run dashboard.py   # 대시보드 (브라우저)
```

데이터 파일 기본 경로: `data/monitor.db`, `data/btc_snapshots.csv`  
환경변수 `BTC_DATA_DIR` 로 디렉터리 변경 가능.

## GitHub Actions (하루 2회)

저장소 **Settings → Secrets and variables → Actions** 에 다음을 등록합니다.

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

워크플로는 UTC 0시·12시에 `daily_job.py` 를 실행합니다.  
SQLite/CSV는 러너 디스크에만 생성되므로 **영구 저장이 필요하면** 아티팩트 업로드나 외부 DB를 추가로 구성하세요.

## Render — 텔레그램 봇 24시간 실행

1. [Render](https://render.com) 에서 **Background Worker** (또는 유사한 상시 프로세스 타입)를 생성합니다.  
   **Web Service**는 HTTP 포트가 필요하므로, **폴링 전용 봇은 Worker가 적합**합니다.
2. 저장소를 연결하고 다음을 설정합니다.

| 항목 | 값 |
|------|-----|
| Build Command | `pip install -r requirements.txt` |
| Start Command | `python bot.py` |

3. **Environment** 에 추가:

| 변수 | 설명 |
|------|------|
| `TELEGRAM_BOT_TOKEN` | 필수 |
| `ALLOWED_CHAT_IDS` | (선택) 허용할 `chat_id` 를 쉼표로 구분. 비우면 모든 채팅 허용 |
| `UPBIT_MARKET` | 기본 `KRW-BTC` |

4. Render 무료 인스턴스는 **유휴 시 슬립**될 수 있습니다. **항상 켜진 봇**이 필요하면 유료 인스턴스나 다른 호스팅을 검토하세요.

## Render — Streamlit 대시보드 (선택)

1. **Web Service** 로 새 서비스 생성.
2. Build: `pip install -r requirements.txt`  
3. Start: `streamlit run dashboard.py --server.port $PORT --server.address 0.0.0.0`
4. SQLite 파일을 유지하려면 **Persistent Disk** 를 마운트하고 `BTC_DATA_DIR` 을 해당 경로로 지정합니다.

## 보안

`.env` 및 Render/GitHub Secrets 에만 토큰을 두고, 저장소에 커밋하지 마세요.
