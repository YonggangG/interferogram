"""Zygo screenshot audit mode via displayed wavefront map/colorbar."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Sequence

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import rgb_to_hsv
from PIL import Image
from scipy import ndimage as ndi


@dataclass(frozen=True)
class DisplayWavefrontResult:
    mode: str
    input_file: str
    map_file: str
    colorbar_file: str
    map_bbox: list[int]
    colorbar_bbox: list[int]
    wavelength_nm: float
    calibration_pv_waves: float
    display_calibrated_pv_waves: float
    display_calibrated_rms_waves: float
    display_calibrated_pv_nm_wavefront: float
    display_calibrated_rms_nm_wavefront: float
    display_calibrated_pv_nm_surface_reflection: float
    display_calibrated_rms_nm_surface_reflection: float
    valid_display_pixels: int
    calibrated_map_image: str
    metrics_json: str
    caution: str


def _rgb(path: Path) -> np.ndarray:
    return np.asarray(Image.open(path).convert("RGB"), dtype=float) / 255.0


def _colorfulness_mask(image: np.ndarray) -> np.ndarray:
    hsv = rgb_to_hsv(image)
    mask = (hsv[..., 1] > 0.18) & (hsv[..., 2] > 0.12)
    mask = ndi.binary_fill_holes(mask)
    mask = ndi.binary_opening(mask, iterations=1)
    mask = ndi.binary_closing(mask, iterations=2)
    return mask.astype(bool)


def _colorbar_lut(colorbar: np.ndarray) -> np.ndarray:
    hsv = rgb_to_hsv(colorbar)
    colored = (hsv[..., 1] > 0.2) & (hsv[..., 2] > 0.15)
    rows = []
    for y in range(colorbar.shape[0]):
        cols = np.where(colored[y])[0]
        rows.append(np.median(colorbar[y, cols], axis=0) if cols.size else [np.nan, np.nan, np.nan])
    lut = np.asarray(rows, dtype=float)
    valid = np.isfinite(lut[:, 0])
    if valid.sum() < 10:
        raise RuntimeError("Could not extract enough colorbar pixels")
    y = np.arange(lut.shape[0])
    for c in range(3):
        lut[:, c] = np.interp(y, y[valid], lut[valid, c])
    return lut


def _map_to_relative_values(map_image: np.ndarray, colorbar_image: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mask = _colorfulness_mask(map_image)
    lut = _colorbar_lut(colorbar_image)
    pixels = map_image.reshape(-1, 3)
    distances = ((pixels[:, None, :] - lut[None, :, :]) ** 2).sum(axis=2)
    nearest_y = np.argmin(distances, axis=1).reshape(map_image.shape[:2])
    relative = 1.0 - nearest_y / max(len(lut) - 1, 1)
    return np.where(mask, relative, np.nan), mask


def _robust_pv_scale(relative: np.ndarray, reference_pv: float) -> np.ndarray:
    vals = relative[np.isfinite(relative)]
    lo, hi = np.nanpercentile(vals, [1, 99])
    if hi <= lo:
        raise RuntimeError("Invalid display map range")
    return (relative - lo) / (hi - lo) * reference_pv


def _save_map(path: Path, arr: np.ndarray, title: str) -> None:
    plt.figure(figsize=(4.5, 3.5))
    plt.imshow(arr, cmap="RdBu_r")
    plt.colorbar(label="waves")
    plt.title(title)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()


def analyze_zygo_display_screenshot(
    image_path: str | Path,
    output_dir: str | Path,
    map_bbox: Sequence[int],
    colorbar_bbox: Sequence[int],
    calibration_pv_waves: float,
    wavelength_nm: float = 633.0,
) -> DisplayWavefrontResult:
    """Audit a Zygo screenshot by decoding the rendered wavefront map colors.

    P-V is used as the calibration anchor, so this route is for screenshot audit
    and approximate map reconstruction, not independent metrology.
    """
    image_path = Path(image_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    image = Image.open(image_path).convert("RGB")
    map_box = list(map(int, map_bbox))
    colorbar_box = list(map(int, colorbar_bbox))
    map_file = output_dir / "zygo_wavefront_display.png"
    colorbar_file = output_dir / "zygo_colorbar.png"
    image.crop(tuple(map_box)).save(map_file)
    image.crop(tuple(colorbar_box)).save(colorbar_file)

    relative, mask = _map_to_relative_values(_rgb(map_file), _rgb(colorbar_file))
    calibrated = _robust_pv_scale(relative, calibration_pv_waves)
    vals = calibrated[np.isfinite(calibrated)]
    pv = float(np.nanpercentile(vals, 99) - np.nanpercentile(vals, 1))
    rms = float(np.nanstd(vals - np.nanmean(vals)))
    calibrated_map = output_dir / "display_calibrated_map.png"
    mask_file = output_dir / "display_mask.png"
    _save_map(calibrated_map, calibrated, "Display-calibrated Zygo wavefront")
    plt.imsave(mask_file, mask, cmap="gray")

    result = DisplayWavefrontResult(
        mode="zygo_screenshot_audit",
        input_file=str(image_path),
        map_file=str(map_file),
        colorbar_file=str(colorbar_file),
        map_bbox=map_box,
        colorbar_bbox=colorbar_box,
        wavelength_nm=wavelength_nm,
        calibration_pv_waves=calibration_pv_waves,
        display_calibrated_pv_waves=pv,
        display_calibrated_rms_waves=rms,
        display_calibrated_pv_nm_wavefront=pv * wavelength_nm,
        display_calibrated_rms_nm_wavefront=rms * wavelength_nm,
        display_calibrated_pv_nm_surface_reflection=pv * wavelength_nm / 2,
        display_calibrated_rms_nm_surface_reflection=rms * wavelength_nm / 2,
        valid_display_pixels=int(np.isfinite(calibrated).sum()),
        calibrated_map_image=str(calibrated_map),
        metrics_json=str(output_dir / "metrics.json"),
        caution="Screenshot audit mode: P-V is calibration input; use for legacy extraction/sanity checks, not independent metrology.",
    )
    (output_dir / "metrics.json").write_text(json.dumps(asdict(result), indent=2), encoding="utf-8")
    return result
