# Interferogram Flatness Analyzer

A Python/FastAPI service for estimating flatness parameters from interferogram images, focused on rectangular-aperture optics such as hexagon scanning mirror faces.

> Current status: engineering prototype. Use for R&D, validation, and workflow development. Production metrology requires calibration with raw interferometer data and known reference results.

## Features

- **Raw/direct fringe mode**
  - FFT carrier demodulation from direct fringe images
  - phase unwrapping
  - rectangular low-order fitting
  - P-V, RMS, Power, and Irregularity estimates
  - diagnostic report image generation

- **Zygo screenshot audit mode**
  - crop rendered Zygo wavefront map and colorbar
  - reconstruct approximate displayed wavefront map
  - extract display-derived metrics for legacy screenshot review

- **Deployment options**
  - Linux / Windows Python source mode
  - Docker container
  - Portainer stack
  - FastAPI web service
  - CLI

## Example diagnostic report

The raw-fringe mode generates a diagnostic report with the selected fringe ROI, wavefront map, residual map, and metrics.

![Example diagnostic report](docs/assets/example_diagnostic_report.png)

## Quick start: Python source mode

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
uvicorn iflat.api:app --host 127.0.0.1 --port 8000
```

Open:

```text
http://127.0.0.1:8000/docs
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

## CLI examples

### Raw/direct fringe mode

```bash
iflat raw-fringe path/to/fringe.jpg \
  --bbox 108,116,208,199 \
  --wavelength-nm 633 \
  --out reports/example_raw
```

### Zygo screenshot audit mode

```bash
iflat zygo-screenshot path/to/Zygo0.png \
  --map-bbox 122,136,748,710 \
  --colorbar-bbox 900,66,927,804 \
  --pv-waves 0.200 \
  --wavelength-nm 633 \
  --out reports/example_zygo
```

## API endpoints

### `POST /analyze/raw-fringe`

Multipart fields:

- `file`: fringe image
- `bbox`: optional `x1,y1,x2,y2`; recommended for photographed images
- `wavelength_nm`: default `633.0`
- `values_are`: default `wavefront_error`

Example:

```bash
curl -X POST http://127.0.0.1:8000/analyze/raw-fringe \
  -F "file=@example-fringe.jpg" \
  -F "bbox=108,116,208,199" \
  -F "wavelength_nm=633"
```

### `POST /audit/zygo-screenshot`

Multipart fields:

- `file`: Zygo screenshot image
- `map_bbox`: wavefront map bbox `x1,y1,x2,y2`
- `colorbar_bbox`: colorbar bbox `x1,y1,x2,y2`
- `calibration_pv_waves`: displayed Zygo P-V in waves
- `wavelength_nm`: default `633.0`

Example:

```bash
curl -X POST http://127.0.0.1:8000/audit/zygo-screenshot \
  -F "file=@Zygo0.png" \
  -F "map_bbox=122,136,748,710" \
  -F "colorbar_bbox=900,66,927,804" \
  -F "calibration_pv_waves=0.200" \
  -F "wavelength_nm=633"
```

## Docker

Build and run locally:

```bash
docker build --network=host -t interferogram-flatness:0.1.0 .
docker run --rm -p 8000:8000 -e IFLAT_RUN_ROOT=/data/reports interferogram-flatness:0.1.0
```

Or use Docker Compose:

```bash
docker compose up -d --build
```

## Portainer

Use `docker-compose.yml` from a Git repository, or load a prebuilt image and deploy with `docker-compose.portainer.yml`.

See: [`docs/docker_portainer_deployment.md`](docs/docker_portainer_deployment.md)

## Windows

Windows source mode and Docker Desktop mode are documented here:

[`docs/windows_run_guide.md`](docs/windows_run_guide.md)

## Documentation

- [`docs/package_api.md`](docs/package_api.md)
- [`docs/docker_portainer_deployment.md`](docs/docker_portainer_deployment.md)
- [`docs/windows_run_guide.md`](docs/windows_run_guide.md)
- [`docs/technical_design.md`](docs/technical_design.md)
- [`docs/validation_protocol.md`](docs/validation_protocol.md)

Chinese README: [`README.zh-CN.md`](README.zh-CN.md)

## Important limitations

- Raw/direct fringe mode is prototype-level unless the input is calibrated raw interferometer intensity data.
- Photographed fringe images may be biased by perspective, gamma, saturation, compression, and lighting.
- Zygo screenshot audit mode is not independent metrology; P-V is used as a calibration anchor for the rendered color map.
- Zernike-equivalent output is planned but not yet finalized in the public API.

## License

License file is not finalized yet. Add a license before broad external reuse.
