@echo off
REM Start FastAPI service from Windows Command Prompt.
REM Run setup_windows.ps1 first.

IF NOT EXIST .venv\Scripts\activate.bat (
  echo Virtual environment not found. Run scripts\windows\setup_windows.ps1 first.
  exit /b 1
)

call .venv\Scripts\activate.bat
if not exist reports\api_runs mkdir reports\api_runs
set IFLAT_RUN_ROOT=%CD%\reports\api_runs
echo Starting API at http://127.0.0.1:8000
echo Open docs: http://127.0.0.1:8000/docs
uvicorn iflat.api:app --host 127.0.0.1 --port 8000
