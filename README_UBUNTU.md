# BTC Monitor — Ubuntu Server 운영 가이드

N100/N5095 미니PC Ubuntu Server 26.04에서 24시간 무중단 BTC 모니터링 서버를 운영하기 위한 가이드입니다.

## 시스템 요구사항

| 항목 | 최소 | 권장 |
|------|------|------|
| OS | Ubuntu 24.04 LTS | Ubuntu 26.04 |
| CPU | x86_64 1코어 | N100/N5095 |
| RAM | 512MB | 2GB+ |
| 디스크 | 1GB 여유 | 5GB+ |
| Python | 3.10+ | 3.14 (시스템 기본) |
| 네트워크 | 인터넷 연결 필수 | — |

## 아키텍처

```
systemd
├── btc-monitor.service        ← local_monitor.py (30분 루프)
│   ├── 스냅샷 수집 (Upbit, CoinGecko, Alternative.me)
│   ├── 120/200일선 돌파 감지 → Telegram 알림
│   ├── 정기 리포트 (08:00, 20:00 KST)
│   └── SQLite/CSV 저장
│
└── btc-bot.service            ← bot.py (Telegram polling)
    └── /btc 명령어 → 실시간 스냅샷 + 차트 응답
```

## 빠른 설치 (원클릭)

```bash
# 1. 프로젝트 클론
git clone https://github.com/your-repo/bitcoin-monitor.git
cd bitcoin-monitor

# 2. 설치 (apt + venv + systemd 한 번에)
sudo ./install.sh

# 3. 환경변수 설정
nano .env
# TELEGRAM_BOT_TOKEN=your_token
# TELEGRAM_CHAT_ID=your_chat_id

# 4. 서비스 시작
sudo systemctl enable --now btc-monitor
sudo systemctl enable --now btc-bot
```

끝. 서버 재부팅 시 자동으로 시작됩니다.

## 수동 설치

### 1. 시스템 패키지

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip python3-dev \
                    build-essential pkg-config tzdata locales
```

### 2. 로케일 & 타임존

```bash
sudo locale-gen ko_KR.UTF-8
sudo update-locale LANG=ko_KR.UTF-8
sudo timedatectl set-timezone Asia/Seoul
```

### 3. Python 가상환경

```bash
cd /path/to/bitcoin-monitor
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. 환경변수

```bash
cp .env.example .env
nano .env
```

필수 항목:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

### 5. 테스트 실행

```bash
source venv/bin/activate
python daily_job.py     # 단발성 스냅샷 + Telegram 전송 테스트
python bot.py           # Telegram 봇 테스트 (Ctrl+C로 종료)
```

### 6. systemd 서비스 등록

```bash
# 서비스 파일의 경로/유저 치환 후 복사
sudo sed \
  -e "s|__PROJECT_DIR__|$(pwd)|g" \
  -e "s|__USER__|$(whoami)|g" \
  -e "s|__GROUP__|$(id -gn)|g" \
  btc-monitor.service > /tmp/btc-monitor.service

sudo sed \
  -e "s|__PROJECT_DIR__|$(pwd)|g" \
  -e "s|__USER__|$(whoami)|g" \
  -e "s|__GROUP__|$(id -gn)|g" \
  btc-bot.service > /tmp/btc-bot.service

sudo mv /tmp/btc-monitor.service /etc/systemd/system/
sudo mv /tmp/btc-bot.service /etc/systemd/system/

sudo systemctl daemon-reload
sudo systemctl enable --now btc-monitor
sudo systemctl enable --now btc-bot
```

## 운영 명령어

### 서비스 관리

```bash
# 상태 확인
sudo systemctl status btc-monitor
sudo systemctl status btc-bot

# 재시작
sudo systemctl restart btc-monitor
sudo systemctl restart btc-bot

# 중지
sudo systemctl stop btc-monitor
sudo systemctl stop btc-bot

# 부팅 시 자동 시작 해제
sudo systemctl disable btc-monitor
sudo systemctl disable btc-bot
```

### 로그 확인

```bash
# 실시간 로그 (journald)
journalctl -u btc-monitor -f
journalctl -u btc-bot -f

# 최근 100줄
journalctl -u btc-monitor -n 100

# 오늘 로그만
journalctl -u btc-monitor --since today

# 파일 로그 (rotation 적용)
tail -f logs/monitor.log
tail -f logs/bot.log

# 오류만
journalctl -u btc-monitor -p err
```

### 데이터 확인

```bash
# SQLite 조회
sqlite3 data/monitor.db "SELECT * FROM snapshots ORDER BY id DESC LIMIT 5;"

# CSV 확인
tail -5 data/btc_snapshots.csv
```

## 트러블슈팅

### 서비스가 시작되지 않을 때

```bash
# 상세 로그 확인
journalctl -u btc-monitor -xe

# 수동 실행으로 오류 확인
cd /path/to/bitcoin-monitor
source venv/bin/activate
python local_monitor.py
```

### Telegram 전송 실패

1. `.env`의 `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` 확인
2. 서버에서 Telegram API 접근 가능한지 확인:
   ```bash
   curl -s "https://api.telegram.org/bot<YOUR_TOKEN>/getMe"
   ```
3. 방화벽 확인:
   ```bash
   sudo ufw status
   sudo ufw allow out 443/tcp  # HTTPS 아웃바운드
   ```

### 메모리 부족

```bash
# 현재 메모리 사용량
systemctl status btc-monitor | grep Memory

# 메모리 제한 조정 (필요 시)
sudo systemctl edit btc-monitor
# [Service]
# MemoryMax=768M
```

### pip install 실패

```bash
# 시스템 빌드 도구 확인
sudo apt install -y python3-dev build-essential pkg-config

# venv 재생성
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 업데이트

```bash
cd /path/to/bitcoin-monitor

# 코드 업데이트
git pull

# 의존성 업데이트
source venv/bin/activate
pip install -r requirements.txt

# 서비스 재시작
sudo systemctl restart btc-monitor btc-bot
```

## Docker (선택사항)

systemd 대신 Docker를 사용할 수도 있습니다. N100 미니PC에서는 systemd가 더 적합하지만,
여러 서버에 배포하거나 격리가 필요한 경우 유용합니다.

```bash
# 모니터 실행
docker build -t btc-monitor .
docker run -d \
  --name btc-monitor \
  --restart=always \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  btc-monitor

# 봇 실행 (별도 컨테이너)
docker run -d \
  --name btc-bot \
  --restart=always \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  btc-monitor python3 bot.py
```

## 안정성 설계

이 시스템은 24/7 무중단 운영을 위해 다음 안정성 기능이 내장되어 있습니다:

| 항목 | 구현 |
|------|------|
| 프로세스 크래시 | systemd `Restart=always` (10초 후 재시작) |
| 서버 재부팅 | systemd `enable` → 부팅 시 자동 시작 |
| API 일시 장애 | `urllib3.Retry` 자동 재시도 (3회, 지수 백오프) |
| Telegram 전송 실패 | 3회 재시도 (2s→4s→8s) |
| 메모리 누수 | `gc.collect()` 주기 호출 + systemd `MemoryMax` |
| 로그 무한 증가 | `RotatingFileHandler` (10MB × 5) + journald |
| Graceful shutdown | SIGTERM 핸들링 → 안전한 종료 |
| 보안 | systemd `NoNewPrivileges`, `ProtectSystem=strict` |
