# Start FastAPI service on Windows PowerShell
# Run from the project root:
#   powershell -ExecutionPolicy Bypass -File scripts\windows\start_api.ps1

$ErrorActionPreference = "Stop"

if (!(Test-Path ".\.venv\Scripts\Activate.ps1")) {
  Write-Error "Virtual environment not found. Run scripts\windows\setup_windows.ps1 first."
}

. .\.venv\Scripts\Activate.ps1

if (!(Test-Path ".\reports\api_runs")) {
  New-Item -ItemType Directory -Path ".\reports\api_runs" | Out-Null
}

$env:IFLAT_RUN_ROOT = (Resolve-Path ".\reports\api_runs").Path
Write-Host "[iflat] Starting API at http://127.0.0.1:8000"
Write-Host "[iflat] Open docs: http://127.0.0.1:8000/docs"
uvicorn iflat.api:app --host 127.0.0.1 --port 8000
