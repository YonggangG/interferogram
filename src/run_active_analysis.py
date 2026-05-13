"""Run second-pass analysis on tight active-fringe aperture crops."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from fourier_phase import extract_phase_fft
from metrics import fit_polynomial

ROOT = Path(__file__).resolve().parents[1]
ACTIVE_DIR = ROOT / "data/processed/fringe_active_aperture"
OUT_DIR = ROOT / "reports/active_fft_analysis"


def edge_mask(shape: tuple[int, int], margin: int = 3) -> np.ndarray:
    mask = np.ones(shape, dtype=bool)
    mask[:margin, :] = False
    mask[-margin:, :] = False
    mask[:, :margin] = False
    mask[:, -margin:] = False
    return mask


def pv_rms(values: np.ndarray) -> tuple[float, float]:
    values = values[np.isfinite(values)]
    return float(np.nanmax(values) - np.nanmin(values)), float(np.nanstd(values - np.nanmean(values)))


def save_map(path: Path, arr: np.ndarray, title: str) -> None:
    plt.figure(figsize=(4.5, 3.5))
    plt.imshow(arr, cmap="RdBu_r")
    plt.colorbar(label="waves")
    plt.title(title)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def analyze_one(path: Path) -> dict[str, float | int | str]:
    gray = np.asarray(Image.open(path).convert("L"), dtype=float)
    mask = edge_mask(gray.shape)

    best = None
    for radius in range(4, 31, 2):
        result = extract_phase_fft(gray, filter_radius_px=radius, mask=mask)
        wf = result.wavefront_waves
        wf = wf - np.nanmean(wf[mask])

        tilt_fit, _ = fit_polynomial(wf, mask, terms=("piston", "tilt_x", "tilt_y"))
        tilt_removed = wf - tilt_fit
        pv_tilt, rms_tilt = pv_rms(tilt_removed[mask])

        power_fit, coeffs = fit_polynomial(wf, mask, terms=("piston", "tilt_x", "tilt_y", "power_x", "power_y"))
        residual = wf - power_fit
        irregularity, residual_rms = pv_rms(residual[mask])

        # Generic no-reference heuristic: prefer compact residual after removing
        # tilt/power, but avoid over-wide filters by adding a mild radius penalty.
        score = irregularity + 0.002 * radius
        candidate = (score, radius, result, wf, tilt_removed, residual, pv_tilt, rms_tilt, irregularity, residual_rms, coeffs)
        if best is None or score < best[0]:
            best = candidate

    assert best is not None
    _, radius, result, wf, tilt_removed, residual, pv_tilt, rms_tilt, irregularity, residual_rms, coeffs = best
    stem = path.stem
    save_map(OUT_DIR / f"{stem}_wavefront.png", wf, f"{stem} wavefront")
    save_map(OUT_DIR / f"{stem}_tilt_removed.png", tilt_removed, f"{stem} tilt removed")
    save_map(OUT_DIR / f"{stem}_residual.png", residual, f"{stem} residual")
    return {
        "file": path.name,
        "selected_radius": radius,
        "carrier_peak_y": result.carrier_peak[0],
        "carrier_peak_x": result.carrier_peak[1],
        "pv_after_tilt_waves": pv_tilt,
        "rms_after_tilt_waves": rms_tilt,
        "irregularity_after_tilt_power_waves": irregularity,
        "residual_rms_waves": residual_rms,
        "power_x_coeff": float(coeffs.get("power_x", 0.0)),
        "power_y_coeff": float(coeffs.get("power_y", 0.0)),
        "power_mean_coeff": float((coeffs.get("power_x", 0.0) + coeffs.get("power_y", 0.0)) / 2),
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = [analyze_one(path) for path in sorted(ACTIVE_DIR.glob("Zygo*_active.png"))]
    csv_path = OUT_DIR / "active_fft_metrics.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(csv_path)


if __name__ == "__main__":
    main()
