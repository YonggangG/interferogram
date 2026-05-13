# Interferogram Flatness Analyzer

A Python/FastAPI service for estimating flatness parameters from interferogram images, focused on rectangular-aperture optics such as hexagon scanning mirror faces.

> Current status: engineering prototype. Use for R&D, validation, and workflow development. Production metrology requires calibration with raw interferometer data and known reference results.

## Features

- **Raw/direct fringe mode**: FFT carrier demodulation, phase unwrap, rectangular low-order fitting, P-V/RMS/Power/Irregularity estimates, and diagnostic report images.
- **Zygo screenshot audit mode**: crop rendered Zygo wavefront map + colorbar, reconstruct approximate displayed wavefront map, and extract display-derived metrics.
- **Deployment options**: Linux source install, Windows source install, Docker/GHCR image, Portainer stack, FastAPI web service, and CLI.

## Example diagnostic report

The raw-fringe mode generates a diagnostic report with the selected fringe ROI, wavefront map, residual map, and metrics.

![Example diagnostic report](docs/assets/example_diagnostic_report.png)

---

## 1. Install the Linux source version from GitHub

Use this when you want to run or modify the Python source directly on a Linux server/workstation.

```bash
git clone https://github.com/YonggangG/interferogram.git
cd interferogram
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -e .
```

Start the web service:

```bash
uvicorn iflat.api:app --host 0.0.0.0 --port 8000
```

Open:

```text
http://SERVER_IP:8000/docs
```

Health check:

```bash
curl http://SERVER_IP:8000/health
```

Expected:

```json
{"status":"ok"}
```

---

## 2. Install the Linux Docker version from GitHub / GHCR

A GitHub Actions workflow publishes the container image to GitHub Container Registry:

```text
ghcr.io/yonggangg/interferogram:latest
ghcr.io/yonggangg/interferogram:0.1.1
```

Pull and run:

```bash
docker pull ghcr.io/yonggangg/interferogram:latest
docker run -d \
  --name interferogram \
  --restart unless-stopped \
  -p 8000:8000 \
  -e IFLAT_RUN_ROOT=/data/reports \
  -v iflat_reports:/data/reports \
  -v iflat_uploads:/data/uploads \
  ghcr.io/yonggangg/interferogram:latest
```

Open:

```text
http://SERVER_IP:8000/docs
```

If the GHCR image is not available yet, build from GitHub source:

```bash
git clone https://github.com/YonggangG/interferogram.git
cd interferogram
docker build --network=host -t interferogram-flatness:0.1.1 .
docker run --rm -p 8000:8000 interferogram-flatness:0.1.1
```

---

## 3. Portainer stack YAML from GitHub deployment

In Portainer:

1. Go to **Stacks** → **Add stack**.
2. Choose **Web editor**.
3. Paste this YAML.
4. Deploy the stack.

```yaml
services:
  interferogram:
    image: ghcr.io/yonggangg/interferogram:latest
    container_name: interferogram
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      IFLAT_RUN_ROOT: /data/reports
    volumes:
      - iflat_reports:/data/reports
      - iflat_uploads:/data/uploads
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3).read()"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 20s

volumes:
  iflat_reports:
  iflat_uploads:
```

Alternatively, deploy directly from the GitHub repository in Portainer:

- Repository URL: `https://github.com/YonggangG/interferogram.git`
- Branch: `main`
- Compose path: `docker-compose.yml`

---

## Quick CLI examples

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

## Windows

Windows source mode and Docker Desktop mode are documented here:

[`docs/windows_run_guide.md`](docs/windows_run_guide.md)

## Documentation

- [`README.zh-CN.md`](README.zh-CN.md)
- [`docs/package_api.md`](docs/package_api.md)
- [`docs/docker_portainer_deployment.md`](docs/docker_portainer_deployment.md)
- [`docs/windows_run_guide.md`](docs/windows_run_guide.md)
- [`docs/technical_design.md`](docs/technical_design.md)
- [`docs/validation_protocol.md`](docs/validation_protocol.md)

## Important limitations

- Raw/direct fringe mode is prototype-level unless the input is calibrated raw interferometer intensity data.
- Photographed fringe images may be biased by perspective, gamma, saturation, compression, and lighting.
- Zygo screenshot audit mode is not independent metrology; P-V is used as a calibration anchor for the rendered color map.
- Zernike-equivalent output is planned but not yet finalized in the public API.

## License

License file is not finalized yet. Add a license before broad external reuse.
