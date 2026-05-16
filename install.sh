#!/usr/bin/env bash
# ============================================================
# install.sh — Ubuntu Server 26.04 용 BTC Monitor 설치 스크립트
#
# 사용법:
#   chmod +x install.sh
#   sudo ./install.sh
# ============================================================
set -euo pipefail

# ── 색상 출력 ──────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { echo -e "${GREEN}[INFO]${NC} $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*"; }

# ── root 확인 ──────────────────────────────────────────────
if [[ $EUID -ne 0 ]]; then
    error "이 스크립트는 root 권한이 필요합니다. sudo ./install.sh 로 실행하세요."
    exit 1
fi

# ── 프로젝트 경로 ──────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

# 실행 유저 (sudo 호출한 원래 유저)
REAL_USER="${SUDO_USER:-$(whoami)}"
REAL_GROUP="$(id -gn "$REAL_USER")"

info "프로젝트 경로: $PROJECT_DIR"
info "실행 유저: $REAL_USER"

# ── 1. apt 패키지 설치 ─────────────────────────────────────
info "[1/6] 시스템 패키지 설치…"
apt-get update -qq
apt-get install -y -qq \
    python3 \
    python3-venv \
    python3-pip \
    python3-dev \
    build-essential \
    pkg-config \
    tzdata \
    locales \
    > /dev/null

# ── 2. 로케일 / 타임존 ────────────────────────────────────
info "[2/6] 로케일 & 타임존 설정…"
locale-gen ko_KR.UTF-8 > /dev/null 2>&1 || true
update-locale LANG=ko_KR.UTF-8 > /dev/null 2>&1 || true

CURRENT_TZ="$(timedatectl show --property=Timezone --value 2>/dev/null || echo '')"
if [[ "$CURRENT_TZ" != "Asia/Seoul" ]]; then
    warn "현재 타임존: $CURRENT_TZ → Asia/Seoul 로 변경합니다."
    timedatectl set-timezone Asia/Seoul
fi

info "[3/6] 절전/대기 모드 비활성화…"
systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target > /dev/null 2>&1 || true

mkdir -p /etc/systemd/logind.conf.d
cat > /etc/systemd/logind.conf.d/99-btc-monitor-no-sleep.conf <<'EOF'
[Login]
IdleAction=ignore
HandleLidSwitch=ignore
HandleLidSwitchExternalPower=ignore
HandleLidSwitchDocked=ignore
EOF

systemctl restart systemd-logind.service > /dev/null 2>&1 || warn "systemd-logind 재시작 실패 — 재부팅 후 절전 방지 설정이 적용됩니다."

# ── 3. Python venv 생성 ───────────────────────────────────
info "[4/6] Python 가상환경 생성…"
VENV_DIR="$PROJECT_DIR/venv"

if [[ -d "$VENV_DIR" ]]; then
    warn "기존 venv 발견 — 재사용합니다. 새로 만들려면: rm -rf $VENV_DIR"
else
    sudo -u "$REAL_USER" python3 -m venv "$VENV_DIR"
fi

sudo -u "$REAL_USER" "$VENV_DIR/bin/pip" install -U pip -q
sudo -u "$REAL_USER" "$VENV_DIR/bin/pip" install -r "$PROJECT_DIR/requirements.txt" -q

PYTHON_VER="$("$VENV_DIR/bin/python3" --version 2>&1)"
info "Python 버전: $PYTHON_VER"

# ── 4. 디렉터리 & 권한 ────────────────────────────────────
info "[5/6] 디렉터리 생성 & 권한 설정…"
mkdir -p "$PROJECT_DIR/data" "$PROJECT_DIR/logs"
chown -R "$REAL_USER:$REAL_GROUP" "$PROJECT_DIR/data" "$PROJECT_DIR/logs"
chmod +x "$PROJECT_DIR/run.sh" "$PROJECT_DIR/run_bot.sh"

# ── 5. systemd 서비스 설치 ─────────────────────────────────
info "[6/6] systemd 서비스 설치…"

# btc-monitor.service 에 경로/유저 치환
for svc in btc-monitor.service btc-bot.service; do
    SVC_SRC="$PROJECT_DIR/$svc"
    SVC_DST="/etc/systemd/system/$svc"

    if [[ ! -f "$SVC_SRC" ]]; then
        warn "$svc 파일이 없습니다 — 건너뜁니다."
        continue
    fi

    sed \
        -e "s|__PROJECT_DIR__|$PROJECT_DIR|g" \
        -e "s|__USER__|$REAL_USER|g" \
        -e "s|__GROUP__|$REAL_GROUP|g" \
        "$SVC_SRC" > "$SVC_DST"

    info "$svc → $SVC_DST"
done

systemctl daemon-reload

# ── .env 확인 ──────────────────────────────────────────────
ENV_FILE="$PROJECT_DIR/.env"
if [[ ! -f "$ENV_FILE" ]]; then
    warn ".env 파일이 없습니다. .env.example 을 복사합니다."
    sudo -u "$REAL_USER" cp "$PROJECT_DIR/.env.example" "$ENV_FILE"
    warn ">>> $ENV_FILE 를 편집하여 TELEGRAM_BOT_TOKEN 등을 설정하세요!"
fi

# ── 완료 ───────────────────────────────────────────────────
echo ""
info "=== 설치 완료 ==="
echo ""
echo "다음 단계:"
echo "  1. .env 파일 편집:"
echo "     nano $ENV_FILE"
echo ""
echo "  2. 서비스 시작 & 부팅 시 자동 실행:"
echo "     sudo systemctl enable --now btc-monitor"
echo "     sudo systemctl enable --now btc-bot"
echo ""
echo "  3. 상태 확인:"
echo "     sudo systemctl status btc-monitor"
echo "     sudo systemctl status btc-bot"
echo ""
echo "  4. 로그 확인:"
echo "     journalctl -u btc-monitor -f"
echo "     journalctl -u btc-bot -f"
echo ""
