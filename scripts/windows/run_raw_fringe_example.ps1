# Example CLI run for raw/direct fringe mode on Windows.
# Edit the image path and bbox before use.

$ErrorActionPreference = "Stop"
. .\.venv\Scripts\Activate.ps1

$image = "data\raw\single_fringe\boss_fringe_20260513.jpg"
$out = "reports\windows_raw_example"
$bbox = "108,116,208,199"

iflat raw-fringe $image --bbox $bbox --wavelength-nm 633 --out $out
Write-Host "Report saved under $out"
