"""Analyze screenshot-displayed Zygo wavefront maps via colorbar lookup.

This is not a replacement for raw phase/intensity data. It converts the rendered
color display into a relative scalar map, then calibrates the scalar range using
OCR-extracted Zygo P-V. RMS from this route is therefore a display-derived
sanity check, not an independent metrology result.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import rgb_to_hsv
from PIL import Image
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
DISPLAY_DIR = ROOT / "data/processed/zygo_wavefront_display"
MANIFEST = ROOT / "data/raw/zygo_screenshots/validation_manifest.json"
OUT_DIR = ROOT / "reports/display_wavefront_analysis"


def rgb(path: Path) -> np.ndarray:
    return np.asarray(Image.open(path).convert("RGB"), dtype=float) / 255.0


def colorfulness_mask(image: np.ndarray) -> np.ndarray:
    hsv = rgb_to_hsv(image)
    sat = hsv[..., 1]
    val = hsv[..., 2]
    # Exclude white/gray UI, black background, and labels. Keep saturated map colors.
    mask = (sat > 0.18) & (val > 0.12)
    mask = ndi.binary_fill_holes(mask)
    mask = ndi.binary_opening(mask, iterations=1)
    mask = ndi.binary_closing(mask, iterations=2)
    return mask.astype(bool)


def colorbar_lut(colorbar: np.ndarray) -> np.ndarray:
    """Return top-to-bottom representative RGB colors from a rendered colorbar."""
    hsv = rgb_to_hsv(colorbar)
    sat = hsv[..., 1]
    val = hsv[..., 2]
    colored = (sat > 0.2) & (val > 0.15)
    rows = []
    for y in range(colorbar.shape[0]):
        cols = np.where(colored[y])[0]
        if cols.size:
            # Use the median colored pixel in the row to avoid text/tick marks.
            rows.append(np.median(colorbar[y, cols], axis=0))
        else:
            rows.append([np.nan, np.nan, np.nan])
    lut = np.asarray(rows, dtype=float)
    valid = np.isfinite(lut[:, 0])
    if valid.sum() < 10:
        raise RuntimeError("Could not extract enough colorbar pixels")
    # Fill missing rows by nearest valid interpolation.
    y = np.arange(lut.shape[0])
    for c in range(3):
        lut[:, c] = np.interp(y, y[valid], lut[valid, c])
    return lut


def map_to_relative_values(map_image: np.ndarray, colorbar_image: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mask = colorfulness_mask(map_image)
    lut = colorbar_lut(colorbar_image)
    valid_colors = lut
    h = len(valid_colors)
    pixels = map_image.reshape(-1, 3)
    # Nearest colorbar color. For these small screenshots, brute force is fine.
    distances = ((pixels[:, None, :] - valid_colors[None, :, :]) ** 2).sum(axis=2)
    nearest_y = np.argmin(distances, axis=1).reshape(map_image.shape[:2])
    # Colorbar top is high, bottom is low. Normalize low=0, high=1.
    relative = 1.0 - nearest_y / max(h - 1, 1)
    relative = np.where(mask, relative, np.nan)
    return relative, mask


def save_map(path: Path, arr: np.ndarray, title: str) -> None:
    plt.figure(figsize=(4.5, 3.5))
    plt.imshow(arr, cmap="RdBu_r")
    plt.colorbar(label="relative/calibrated waves")
    plt.title(title)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def robust_pv_scale(relative: np.ndarray, reference_pv: float) -> np.ndarray:
    vals = relative[np.isfinite(relative)]
    lo, hi = np.nanpercentile(vals, [1, 99])
    if hi <= lo:
        return relative * np.nan
    return (relative - lo) / (hi - lo) * reference_pv


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    refs = json.loads(MANIFEST.read_text())["records"]
    rows = []
    for i, ref in enumerate(refs):
        stem = f"Zygo{i}"
        map_image = rgb(DISPLAY_DIR / f"{stem}_wavefront_display.png")
        colorbar_image = rgb(DISPLAY_DIR / f"{stem}_colorbar.png")
        relative, mask = map_to_relative_values(map_image, colorbar_image)
        calibrated = robust_pv_scale(relative, float(ref["pv_waves"]))
        vals = calibrated[np.isfinite(calibrated)]
        pv = float(np.nanpercentile(vals, 99) - np.nanpercentile(vals, 1))
        rms = float(np.nanstd(vals - np.nanmean(vals)))
        save_map(OUT_DIR / f"{stem}_display_relative.png", relative, f"{stem} display relative")
        save_map(OUT_DIR / f"{stem}_display_calibrated.png", calibrated, f"{stem} display calibrated")
        plt.imsave(OUT_DIR / f"{stem}_display_mask.png", mask, cmap="gray")
        rows.append(
            {
                "face_id": ref["face_id"],
                "source": stem,
                "zygo_pv_waves": ref["pv_waves"],
                "display_calibrated_pv_waves": pv,
                "zygo_rms_waves": ref["rms_waves"],
                "display_calibrated_rms_waves": rms,
                "rms_rel_error": (rms - ref["rms_waves"]) / ref["rms_waves"],
                "valid_display_pixels": int(np.isfinite(calibrated).sum()),
                "note": "PV calibrated to Zygo OCR reference using 1-99 percentile display range; RMS is display-derived.",
            }
        )
    out_csv = OUT_DIR / "display_wavefront_metrics.csv"
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(out_csv)


if __name__ == "__main__":
    main()
