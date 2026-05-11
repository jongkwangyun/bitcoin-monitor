@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo [ERROR] .venv not found. Please run setup_venv.bat first.
  pause
  exit /b 1
)
echo [daily_job] Starting...
".venv\Scripts\python.exe" daily_job.py %*
if errorlevel 1 (
  echo.
  echo [ERROR] daily_job.py exited with an error. Check the log above.
)
pause
