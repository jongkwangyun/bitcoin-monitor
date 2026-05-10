@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo [1/3] Python 3.14로 가상환경 .venv 생성...
py -3.14 -m venv .venv
if not exist ".venv\Scripts\python.exe" (
  python -m venv .venv
)
if not exist ".venv\Scripts\python.exe" (
  echo 실패: 3.14 가상환경을 만들 수 없습니다.
  echo - python.org Python 3.14 설치 후 ^`py -3.14^` 또는 ^`python^` 이 동작하는지 확인하세요.
  echo - 예전 .venv 가 남아 있으면: rmdir /s /q .venv 후 다시 실행하세요.
  exit /b 1
)

echo [2/3] pip 업그레이드...
".venv\Scripts\python.exe" -m pip install -U pip
if errorlevel 1 exit /b 1

echo [3/3] requirements.txt 설치...
".venv\Scripts\pip.exe" install -r requirements.txt
if errorlevel 1 exit /b 1

echo.
echo === 완료 ===
echo 가상환경 Python:
".venv\Scripts\python.exe" --version
echo.
echo 다음 중 하나로 실행하세요:
echo   1^) 수동:  .venv\Scripts\activate.bat   ^(또는 PowerShell: .venv\Scripts\Activate.ps1^)
echo           그 다음: python daily_job.py
echo   2^) 배치: run_daily_job.bat , run_bot.bat , run_dashboard.bat
echo.
echo PATH의 다른 python 과 무관하게, 위 방법은 항상 이 폴더의 3.14 가상환경을 씁니다.
pause
