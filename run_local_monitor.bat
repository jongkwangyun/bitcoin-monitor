@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo [ERROR] .venv not found. Please run setup_venv.bat first.
  pause
  exit /b 1
)
echo ============================================
echo  BTC Monitor - 30min interval auto run
echo  Press Ctrl+C to stop
echo ============================================
echo.
".venv\Scripts\python.exe" local_monitor.py %*
if errorlevel 1 (
  echo.
  echo [ERROR] local_monitor.py exited with an error. Check the log above.
)
pause
