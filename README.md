# Bitcoin Monitor (BTC 모니터링 봇)

이 프로젝트는 업비트(Upbit)의 비트코인(KRW-BTC) 가격을 주기적으로 모니터링하여 이동평균선의 돌파 알림과 매일 2회 정기 리포트를 텔레그램으로 전송해 주는 시스템입니다.

## 주요 기능
- **돌파/이탈 필터링 알림**: 일시적인 휩소를 방지하기 위해 120일/200일선 교차 발생 후 30분 간격으로 2회 연속(최소 1시간) 동일 방향 유지 시에만 확정 알림을 발송합니다.
- **정기 리포트 전송**: KST 기준 매일 오전 8시, 오후 8시에 시장 상태 요약 및 차트 리포트를 자동으로 발송합니다.
- **텔레그램 명령어 봇**: `/btc` 명령어를 통해 언제든지 현재 상태 스냅샷 및 차트를 수동으로 조회할 수 있습니다.
- **상태 유지**: GitHub Actions의 Cache 기능을 활용해 이전 상태(`.btc_alert_cache.json`, `.btc_report_state.json`)를 기억합니다.

## 실행 방법 (로컬 환경)

1. **가상환경 설정**
   ```bat
   setup_venv.bat
   ```
2. **환경변수 설정**
   `.env.example` 파일을 참고하여 `.env` 파일을 만들고 아래 항목을 기입합니다.
   ```env
   TELEGRAM_BOT_TOKEN=당신의_봇_토큰
   TELEGRAM_CHAT_ID=알림을_받을_채팅방_ID
   ```
3. **단발성 실행 (정기 알림 및 돌파 체크용)**
   ```bat
   run_daily_job.bat
   ```
4. **명령어 봇 실행 (24시간 동작)**
   ```bat
   run_bot.bat
   ```

## 실행 방법 (GitHub Actions)
서버 없이 GitHub 저장소의 Actions 스케줄러를 통해 30분 단위로 자동 실행합니다.

1. **GitHub Secrets 설정**
   저장소의 `Settings > Secrets and variables > Actions` 에 `TELEGRAM_BOT_TOKEN`과 `TELEGRAM_CHAT_ID`를 등록합니다.
2. **자동화 동작**
   - `.github/workflows/bitcoin-monitor.yml` 에 의해 매 30분마다(`*/30 * * * *`) `daily_job.py`가 자동으로 실행됩니다.
   - 30분마다 돌파 여부를 체크하고, 시간이 08:xx 나 20:xx 일 경우에는 정기 리포트도 추가로 전송합니다.

## 요구사항 (Requirements)
Windows 환경의 `zoneinfo` 지원을 위한 `tzdata` 패키지가 추가되었습니다.
필요한 패키지(`pandas`, `requests`, `python-telegram-bot`, `streamlit`, `matplotlib`, `tzdata`)는 `requirements.txt`에 명시되어 있습니다.
