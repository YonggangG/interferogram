#!/usr/bin/env bash
set -euo pipefail

curl -X POST http://127.0.0.1:8000/analyze/raw-fringe \
  -F "file=@example-fringe.jpg" \
  -F "bbox=108,116,208,199" \
  -F "wavelength_nm=633"
