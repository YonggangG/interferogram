# Package and API Guide

## Purpose

The project now exposes two formal modes:

1. **Raw/direct fringe mode**
   - For direct interferogram intensity images.
   - Uses FFT carrier demodulation, phase unwrap, rectangular low-order fitting, and metric reporting.

2. **Zygo screenshot audit mode**
   - For existing Zygo screenshots.
   - Crops the rendered wavefront display and colorbar, reconstructs an approximate displayed wavefront map, and reports display-derived metrics.
   - P-V is used as a calibration input, so this is not independent metrology.

## Install locally

```bash
cd /home/xin/.openclaw/workspace/interferogram-flatness
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
```

## CLI usage

### Raw/direct fringe mode

```bash
iflat raw-fringe path/to/fringe.png \
  --bbox 108,116,208,199 \
  --wavelength-nm 633 \
  --out reports/example_raw
```

Outputs include:

- `fringe_crop.png`
- `wavefront_raw.png`
- `tilt_removed.png`
- `residual_irregularity.png`
- `diagnostic_report_with_metrics.png`
- `metrics.json`
- `sweep.csv`

### Zygo screenshot audit mode

```bash
iflat zygo-screenshot path/to/zygo.png \
  --map-bbox 122,136,748,710 \
  --colorbar-bbox 900,66,927,804 \
  --pv-waves 0.200 \
  --wavelength-nm 633 \
  --out reports/example_zygo
```

Outputs include:

- `zygo_wavefront_display.png`
- `zygo_colorbar.png`
- `display_calibrated_map.png`
- `display_mask.png`
- `metrics.json`

## API server

Start server:

```bash
cd /home/xin/.openclaw/workspace/interferogram-flatness
. .venv/bin/activate
uvicorn iflat.api:app --reload --host 127.0.0.1 --port 8000
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

## API endpoints

### `POST /analyze/raw-fringe`

Multipart form fields:

- `file`: image file
- `bbox`: optional `x1,y1,x2,y2`; recommended for photographed or cropped inputs
- `wavelength_nm`: default `633.0`
- `values_are`: default `wavefront_error`

Example:

```bash
curl -X POST http://127.0.0.1:8000/analyze/raw-fringe \
  -F "file=@data/raw/single_fringe/boss_fringe_20260513.jpg" \
  -F "bbox=108,116,208,199" \
  -F "wavelength_nm=633"
```

### `POST /audit/zygo-screenshot`

Multipart form fields:

- `file`: Zygo screenshot image
- `map_bbox`: required `x1,y1,x2,y2` for displayed wavefront map
- `colorbar_bbox`: required `x1,y1,x2,y2` for colorbar
- `calibration_pv_waves`: required Zygo displayed P-V in waves
- `wavelength_nm`: default `633.0`

Example:

```bash
curl -X POST http://127.0.0.1:8000/audit/zygo-screenshot \
  -F "file=@data/raw/zygo_screenshots/Zygo0.png" \
  -F "map_bbox=122,136,748,710" \
  -F "colorbar_bbox=900,66,927,804" \
  -F "calibration_pv_waves=0.200" \
  -F "wavelength_nm=633"
```

## Current limitations

- Raw fringe mode is prototype-level unless the input is a raw/direct interferogram intensity image.
- The default bbox auto-crop is only a fallback; production callers should provide ROI or use a future ROI detection module.
- Zygo screenshot audit mode requires map/colorbar bounding boxes and P-V calibration input.
- OCR is not yet part of the API; current OCR was done by the assistant vision pipeline during dataset preparation.
- Zernike-equivalent coefficient output remains planned; current package focuses on rectangular FFT/metric and display-map audit paths.
