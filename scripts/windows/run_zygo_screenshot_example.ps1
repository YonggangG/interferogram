# Example CLI run for Zygo screenshot audit mode on Windows.
# Edit image path, map bbox, colorbar bbox, and PV before use.

$ErrorActionPreference = "Stop"
. .\.venv\Scripts\Activate.ps1

$image = "data\raw\zygo_screenshots\Zygo0.png"
$out = "reports\windows_zygo_example"
$mapBbox = "122,136,748,710"
$colorbarBbox = "900,66,927,804"
$pvWaves = "0.200"

iflat zygo-screenshot $image --map-bbox $mapBbox --colorbar-bbox $colorbarBbox --pv-waves $pvWaves --wavelength-nm 633 --out $out
Write-Host "Report saved under $out"
