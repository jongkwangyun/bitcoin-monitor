import time
import logging
from datetime import datetime
import traceback
from daily_job import main as daily_job_main

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("local_monitor")

def get_seconds_until_next_period(minutes: int = 30) -> float:
    now = datetime.now()
    # Calculate how many seconds have passed since the start of the hour
    seconds_past_hour = now.minute * 60 + now.second + now.microsecond / 1_000_000
    period_seconds = minutes * 60
    # Next multiple of period_seconds
    next_period = ((seconds_past_hour // period_seconds) + 1) * period_seconds
    wait_seconds = next_period - seconds_past_hour
    return wait_seconds

def run():
    logger.info("Starting local monitor loop (30m interval)...")
    
    # 프로그램 시작 시 즉시 1회 실행
    try:
        logger.info("Running initial check...")
        daily_job_main()
    except Exception as e:
        logger.error(f"Error in daily_job: {e}")
        logger.error(traceback.format_exc())

    while True:
        # 다음 정각 또는 30분까지 대기 (예: 08:00, 08:30, 09:00 ...)
        wait_seconds = get_seconds_until_next_period(30)
        next_time = datetime.fromtimestamp(time.time() + wait_seconds)
        logger.info(f"Waiting for {wait_seconds / 60:.2f} minutes until next check at {next_time.strftime('%H:%M:%S')}...")
        
        time.sleep(wait_seconds)
        
        try:
            logger.info("Running scheduled check...")
            daily_job_main()
        except Exception as e:
            logger.error(f"Error in daily_job: {e}")
            logger.error(traceback.format_exc())

if __name__ == "__main__":
    run()
