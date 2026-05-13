# Docker / Portainer Deployment Guide

## Goal

Run Interferogram Flatness Analyzer as a Docker web service, deployable from Portainer.

API docs:

```text
http://SERVER_IP:8000/docs
```

Health check:

```text
http://SERVER_IP:8000/health
```

## Published image

GitHub Actions publishes the image to GitHub Container Registry:

```text
ghcr.io/yonggangg/interferogram:latest
ghcr.io/yonggangg/interferogram:0.1.1
```

If the image is not visible immediately after a release, check the GitHub Actions page for the `Publish Docker image` workflow.

## Run from GHCR on Linux

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

## Build from GitHub source on Linux

```bash
git clone https://github.com/YonggangG/interferogram.git
cd interferogram
docker build --network=host -t interferogram-flatness:0.1.1 .
docker run --rm -p 8000:8000 interferogram-flatness:0.1.1
```

`--network=host` is optional, but useful on some servers where Docker build DNS is unreliable.

## Portainer Stack YAML using GHCR image

In Portainer:

1. Go to **Stacks** → **Add stack**.
2. Choose **Web editor**.
3. Paste this YAML.
4. Deploy.

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

## Portainer Stack from GitHub repository

If your Portainer instance can access GitHub and build locally:

1. Go to **Stacks** → **Add stack**.
2. Choose **Repository**.
3. Use:

```text
Repository URL: https://github.com/YonggangG/interferogram.git
Branch: main
Compose path: docker-compose.yml
```

4. Deploy.

This method builds from the Dockerfile in the repository.

## API smoke test

```bash
curl http://SERVER_IP:8000/health
```

Expected:

```json
{"status":"ok"}
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

## Production notes

- Put the service behind HTTPS/reverse proxy if exposed outside a trusted LAN.
- Add authentication before internet exposure.
- Use persistent volumes for `/data/reports` and `/data/uploads`.
- For production metrology, prefer raw/direct interferogram intensity images over screenshots.
