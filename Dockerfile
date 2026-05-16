FROM python:3.14-slim

LABEL maintainer="bitcoin-monitor"
LABEL description="BTC Monitor — 30분 간격 모니터링 + Telegram 봇"

# 시스템 패키지 (matplotlib용 최소 의존성)
RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends \
        tzdata \
        locales \
    && locale-gen ko_KR.UTF-8 \
    && rm -rf /var/lib/apt/lists/*

ENV LANG=ko_KR.UTF-8 \
    LC_ALL=ko_KR.UTF-8 \
    TZ=Asia/Seoul \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# 의존성 먼저 (레이어 캐시 활용)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 복사
COPY . .

# non-root 유저
RUN useradd -m -r appuser && \
    mkdir -p /app/data /app/logs && \
    chown -R appuser:appuser /app
USER appuser

# 기본 엔트리포인트: local_monitor.py
# bot.py 는 docker-compose 또는 별도 컨테이너로 실행
CMD ["python3", "local_monitor.py"]
