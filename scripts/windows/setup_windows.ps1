# Setup Interferogram Flatness Analyzer on Windows PowerShell
# Run from the project root:
#   powershell -ExecutionPolicy Bypass -File scripts\windows\setup_windows.ps1

$ErrorActionPreference = "Stop"

Write-Host "[iflat] Checking Python..."
python --version

Write-Host "[iflat] Creating virtual environment .venv ..."
python -m venv .venv

Write-Host "[iflat] Activating virtual environment..."
. .\.venv\Scripts\Activate.ps1

Write-Host "[iflat] Upgrading pip..."
python -m pip install --upgrade pip

Write-Host "[iflat] Installing package in editable mode..."
pip install -e .

Write-Host "[iflat] Setup complete."
Write-Host "Start API with: powershell -ExecutionPolicy Bypass -File scripts\windows\start_api.ps1"
