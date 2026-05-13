# Windows Run Guide

This project can run on Windows in three practical ways:

1. **Windows source/Python mode** — easiest for engineering and testing.
2. **Windows Docker Desktop mode** — same container as server deployment.
3. **Future packaged EXE mode** — possible later with PyInstaller, not yet finalized.

## Recommendation

For now, use **Windows source/Python mode** for local lab use and debugging. Use **Docker Desktop mode** if you want the Windows machine to behave like the server/Portainer deployment.

---

## Option A — Windows source/Python mode

### 1. Install prerequisites

Install:

- Windows 10/11
- Python 3.12 recommended
- Git, optional but useful

During Python installation, check:

```text
Add python.exe to PATH
```

Verify in PowerShell:

```powershell
python --version
```

Expected: Python 3.10+; Python 3.12 preferred.

### 2. Get the project folder

Either clone from Git later, or copy the project folder to Windows, for example:

```text
C:\Users\YOURNAME\interferogram-flatness
```

Open PowerShell in that folder.

### 3. Setup virtual environment

From the project root:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\windows\setup_windows.ps1
```

This creates `.venv` and installs the package with all Python dependencies.

### 4. Start the web API

```powershell
powershell -ExecutionPolicy Bypass -File scripts\windows\start_api.ps1
```

Open browser:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"ok"}
```

### 5. Run CLI examples

Raw/direct fringe example:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\windows\run_raw_fringe_example.ps1
```

Zygo screenshot audit example:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\windows\run_zygo_screenshot_example.ps1
```

Edit the image paths and bounding boxes inside the scripts for real data.

---

## Option B — Windows Docker Desktop mode

Use this if Windows has Docker Desktop installed.

### 1. Install Docker Desktop

Install Docker Desktop for Windows and make sure it is running.

Verify:

```powershell
docker --version
docker compose version
```

### 2. Build and run

From the project root:

```powershell
docker compose build
docker compose up -d
```

Open:

```text
http://127.0.0.1:8000/docs
```

Stop:

```powershell
docker compose down
```

This is close to the server/Portainer deployment model.

---

## Option C — Future Windows EXE mode

A standalone `.exe` is possible with PyInstaller, but not recommended as the first production path because:

- scientific packages make the bundle large,
- FastAPI + image processing packaging needs extra testing,
- Docker/Python modes are easier to update.

A future EXE target could provide:

- `iflat-api.exe` to start the web service,
- `iflat-cli.exe` for command-line processing.

Recommended future command:

```powershell
pyinstaller --onefile --name iflat-api scripts\windows\iflat_api_entry.py
```

This entry script has not been added yet.

---

## API usage on Windows

### Raw/direct fringe mode

Endpoint:

```text
POST /analyze/raw-fringe
```

Fields:

- `file`: fringe image
- `bbox`: optional `x1,y1,x2,y2`
- `wavelength_nm`: default `633`

PowerShell curl example:

```powershell
curl.exe -X POST http://127.0.0.1:8000/analyze/raw-fringe ^
  -F "file=@data\raw\single_fringe\boss_fringe_20260513.jpg" ^
  -F "bbox=108,116,208,199" ^
  -F "wavelength_nm=633"
```

### Zygo screenshot audit mode

Endpoint:

```text
POST /audit/zygo-screenshot
```

Fields:

- `file`: Zygo screenshot
- `map_bbox`: wavefront map bbox `x1,y1,x2,y2`
- `colorbar_bbox`: colorbar bbox `x1,y1,x2,y2`
- `calibration_pv_waves`: Zygo displayed P-V in waves
- `wavelength_nm`: default `633`

PowerShell curl example:

```powershell
curl.exe -X POST http://127.0.0.1:8000/audit/zygo-screenshot ^
  -F "file=@data\raw\zygo_screenshots\Zygo0.png" ^
  -F "map_bbox=122,136,748,710" ^
  -F "colorbar_bbox=900,66,927,804" ^
  -F "calibration_pv_waves=0.200" ^
  -F "wavelength_nm=633"
```

---

## Output location

Windows source/Python mode writes API outputs to:

```text
reports\api_runs\...
```

CLI output location is controlled by `--out`.

Docker Desktop mode writes into Docker volumes unless changed in `docker-compose.yml`.

---

## Troubleshooting

### PowerShell blocks scripts

Use:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\windows\setup_windows.ps1
```

### `python` not found

Reinstall Python and enable "Add python.exe to PATH", or use:

```powershell
py -3.12 --version
```

### Package install is slow

This is normal. `numpy`, `scipy`, `scikit-image`, `opencv-python-headless`, and `matplotlib` are large packages.

### API starts but browser cannot connect

Confirm the terminal says:

```text
Uvicorn running on http://127.0.0.1:8000
```

If port 8000 is occupied, change the port in `scripts\windows\start_api.ps1`.
