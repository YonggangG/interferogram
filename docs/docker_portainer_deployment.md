# Docker / Portainer Deployment Guide

## Goal

Run the Rectangular Interferogram Flatness Analyzer as a web service in Docker, deployable from Portainer.

The service exposes FastAPI endpoints:

- `GET /health`
- `POST /analyze/raw-fringe`
- `POST /audit/zygo-screenshot`
- `GET /runs/{run_id}/{mode}/{filename}`

Interactive API docs are available at:

- `http://SERVER_IP:8000/docs`

## Files

- `Dockerfile` — builds the API service image. It intentionally avoids apt packages and uses headless Python dependencies for server compatibility.
- `.dockerignore` — excludes local venv/data/reports from the image.
- `docker-compose.yml` — local build + run.
- `docker-compose.portainer.yml` — Portainer stack template using an existing image.

## Local build test

```bash
cd /home/xin/.openclaw/workspace/interferogram-flatness
docker compose build
docker compose up -d
curl http://127.0.0.1:8000/health
docker compose down
```

Expected health response:

```json
{"status":"ok"}
```

## Option A: Portainer deploy from Git repository

Best long-term method.

1. Push this project to a Git repository available to the server.
2. In Portainer:
   - Go to **Stacks** → **Add stack**.
   - Choose **Repository**.
   - Set repository URL and branch.
   - Compose path: `docker-compose.yml`.
   - Deploy the stack.
3. Open:
   - `http://SERVER_IP:8000/health`
   - `http://SERVER_IP:8000/docs`

This option lets Portainer build from the Dockerfile.

## Option B: Build image locally, export, import on server

Useful if the server cannot access the project Git repo.

On build machine:

```bash
cd /home/xin/.openclaw/workspace/interferogram-flatness
docker build -t interferogram-flatness:0.1.0 .
docker save interferogram-flatness:0.1.0 | gzip > interferogram-flatness-0.1.0.tar.gz
```

Copy `interferogram-flatness-0.1.0.tar.gz` to the server.

On server:

```bash
gunzip -c interferogram-flatness-0.1.0.tar.gz | docker load
```

Then in Portainer:

1. Go to **Stacks** → **Add stack**.
2. Choose **Web editor**.
3. Paste contents of `docker-compose.portainer.yml`.
4. Deploy.

## Option C: Push to private registry

On build machine:

```bash
docker build -t YOUR_REGISTRY/interferogram-flatness:0.1.0 .
docker push YOUR_REGISTRY/interferogram-flatness:0.1.0
```

Then edit Portainer stack image:

```yaml
image: YOUR_REGISTRY/interferogram-flatness:0.1.0
```

## Volumes

The container uses persistent volumes:

- `iflat_reports:/data/reports`
- `iflat_uploads:/data/uploads`

`IFLAT_RUN_ROOT=/data/reports` controls where API run outputs are written.

## API smoke test

After deployment:

```bash
curl http://SERVER_IP:8000/health
```

Raw fringe example:

```bash
curl -X POST http://SERVER_IP:8000/analyze/raw-fringe \
  -F "file=@example-fringe.jpg" \
  -F "bbox=108,116,208,199" \
  -F "wavelength_nm=633"
```

Zygo screenshot audit example:

```bash
curl -X POST http://SERVER_IP:8000/audit/zygo-screenshot \
  -F "file=@Zygo0.png" \
  -F "map_bbox=122,136,748,710" \
  -F "colorbar_bbox=900,66,927,804" \
  -F "calibration_pv_waves=0.200" \
  -F "wavelength_nm=633"
```

The JSON response includes generated image URLs such as:

- `/runs/{run_id}/raw_fringe/diagnostic_report_with_metrics.png`
- `/runs/{run_id}/zygo_screenshot/display_calibrated_map.png`

## Production notes

- Put the service behind HTTPS/reverse proxy if exposed outside a trusted LAN.
- Consider adding authentication before internet exposure.
- Increase container CPU/RAM if batch image processing is slow.
- For production metrology, prefer raw/direct interferogram intensity images over screenshots.
