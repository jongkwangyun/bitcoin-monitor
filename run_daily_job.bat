@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo 먼저 setup_venv.bat 을 실행하세요.
  exit /b 1
)
".venv\Scripts\python.exe" daily_job.py %*
