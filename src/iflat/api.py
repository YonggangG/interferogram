"""FastAPI service for interferogram flatness analysis."""

from __future__ import annotations

import os
import shutil
import uuid
from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from .display_wavefront import analyze_zygo_display_screenshot
from .raw_fringe import analyze_raw_fringe

APP_ROOT = Path.cwd()
RUN_ROOT = Path(os.environ.get("IFLAT_RUN_ROOT", str(APP_ROOT / "reports/api_runs")))

app = FastAPI(
    title="Rectangular Interferogram Flatness Analyzer",
    version="0.1.0",
    description="Two-mode prototype API: raw/direct fringe analysis and Zygo screenshot audit.",
)


def _parse_bbox(value: str | None, field: str) -> list[int] | None:
    if not value:
        return None
    try:
        parts = [int(float(p.strip())) for p in value.split(",")]
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid {field}; expected x1,y1,x2,y2") from exc
    if len(parts) != 4 or parts[2] <= parts[0] or parts[3] <= parts[1]:
        raise HTTPException(status_code=400, detail=f"Invalid {field}; expected x1,y1,x2,y2")
    return parts


def _save_upload(file: UploadFile, run_dir: Path) -> Path:
    suffix = Path(file.filename or "upload.png").suffix or ".png"
    path = run_dir / f"input{suffix}"
    with path.open("wb") as f:
        shutil.copyfileobj(file.file, f)
    return path


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/analyze/raw-fringe")
def analyze_raw_fringe_endpoint(
    file: UploadFile = File(...),
    bbox: str | None = Form(default=None, description="Optional x1,y1,x2,y2 crop bbox."),
    wavelength_nm: float = Form(default=633.0),
    values_are: str = Form(default="wavefront_error"),
) -> dict:
    """Analyze a direct fringe image.

    Use this for raw/direct interferogram intensity images. For photographed
    images, provide a tight bbox around the useful fringe aperture.
    """
    run_id = uuid.uuid4().hex
    run_dir = RUN_ROOT / run_id / "raw_fringe"
    run_dir.mkdir(parents=True, exist_ok=True)
    input_path = _save_upload(file, run_dir)
    result = analyze_raw_fringe(
        input_path,
        run_dir,
        bbox=_parse_bbox(bbox, "bbox"),
        wavelength_nm=wavelength_nm,
        values_are=values_are,
    )
    data = asdict(result)
    data["run_id"] = run_id
    data["report_url"] = f"/runs/{run_id}/raw_fringe/diagnostic_report_with_metrics.png"
    return data


@app.post("/audit/zygo-screenshot")
def audit_zygo_screenshot_endpoint(
    file: UploadFile = File(...),
    map_bbox: str = Form(..., description="x1,y1,x2,y2 bbox for displayed wavefront map."),
    colorbar_bbox: str = Form(..., description="x1,y1,x2,y2 bbox for colorbar."),
    calibration_pv_waves: float = Form(..., description="Zygo displayed P-V in waves, used for color-map calibration."),
    wavelength_nm: float = Form(default=633.0),
) -> dict:
    """Audit a Zygo screenshot by decoding its rendered wavefront map/colorbar."""
    run_id = uuid.uuid4().hex
    run_dir = RUN_ROOT / run_id / "zygo_screenshot"
    run_dir.mkdir(parents=True, exist_ok=True)
    input_path = _save_upload(file, run_dir)
    map_box = _parse_bbox(map_bbox, "map_bbox")
    colorbar_box = _parse_bbox(colorbar_bbox, "colorbar_bbox")
    assert map_box is not None and colorbar_box is not None
    result = analyze_zygo_display_screenshot(
        input_path,
        run_dir,
        map_bbox=map_box,
        colorbar_bbox=colorbar_box,
        calibration_pv_waves=calibration_pv_waves,
        wavelength_nm=wavelength_nm,
    )
    data = asdict(result)
    data["run_id"] = run_id
    data["calibrated_map_url"] = f"/runs/{run_id}/zygo_screenshot/display_calibrated_map.png"
    return data


@app.get("/runs/{run_id}/{mode}/{filename}")
def get_run_file(run_id: str, mode: str, filename: str) -> FileResponse:
    if mode not in {"raw_fringe", "zygo_screenshot"}:
        raise HTTPException(status_code=404, detail="Unknown mode")
    path = RUN_ROOT / run_id / mode / filename
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path)
