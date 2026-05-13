#!/usr/bin/env bash
set -euo pipefail

curl -X POST http://127.0.0.1:8000/audit/zygo-screenshot \
  -F "file=@Zygo0.png" \
  -F "map_bbox=122,136,748,710" \
  -F "colorbar_bbox=900,66,927,804" \
  -F "calibration_pv_waves=0.200" \
  -F "wavelength_nm=633"
