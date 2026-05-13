"""Run improved FFT demodulation sweep over carrier peaks and sideband filters."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from fourier_phase import extract_phase_fft_at_peak, find_carrier_candidates, prepare_fft_image
from metrics import fit_polynomial

ROOT = Path(__file__).resolve().parents[1]
ACTIVE_DIR = ROOT / "data/processed/fringe_active_aperture"
OUT_DIR = ROOT / "reports/improved_fft_sweep"


def edge_mask(shape: tuple[int, int], margin: int = 3) -> np.ndarray:
    mask = np.ones(shape, dtype=bool)
    mask[:margin, :] = False
    mask[-margin:, :] = False
    mask[:, :margin] = False
    mask[:, -margin:] = False
    return mask


def pv_rms(arr: np.ndarray) -> tuple[float, float]:
    v = arr[np.isfinite(arr)]
    return float(np.nanmax(v) - np.nanmin(v)), float(np.nanstd(v - np.nanmean(v)))


def save_map(path: Path, arr: np.ndarray, title: str) -> None:
    plt.figure(figsize=(4.5, 3.5))
    plt.imshow(arr, cmap="RdBu_r")
    plt.colorbar(label="waves")
    plt.title(title)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def score_solution(pv_tilt: float, rms_tilt: float, irr: float, radius: int) -> float:
    """Reference-free quality heuristic.

    Avoids giant unwrap/ramp solutions, prefers compact residuals and realistic
    PV/RMS scale for these screenshot fringe patches.
    """
    return irr + 0.25 * rms_tilt + 0.03 * max(pv_tilt - 0.8, 0) + 0.002 * radius


def analyze_one(path: Path) -> dict[str, float | int | str]:
    gray = np.asarray(Image.open(path).convert("L"), dtype=float)
    mask = edge_mask(gray.shape)
    prepared = prepare_fft_image(gray, mask=mask)
    spectrum = np.fft.fftshift(np.fft.fft2(prepared))
    candidates = find_carrier_candidates(spectrum, dc_radius=max(5, min(gray.shape) // 18), count=10)

    all_rows = []
    best = None
    for peak in candidates:
        py, px = peak
        angle = np.arctan2(py - gray.shape[0] // 2, px - gray.shape[1] // 2)
        # Try both circular-ish Gaussian and elongated filters along/against sideband.
        for radius in range(3, 19, 1):
            for ratio in (0.45, 0.65, 0.9, 1.0):
                try:
                    result = extract_phase_fft_at_peak(
                        gray,
                        peak=peak,
                        filter_radius_px=radius,
                        mask=mask,
                        method="gaussian",
                        ellipse_ratio=ratio,
                        angle_rad=angle,
                    )
                    wf = result.wavefront_waves - np.nanmean(result.wavefront_waves[mask])
                    tilt_fit, _ = fit_polynomial(wf, mask, terms=("piston", "tilt_x", "tilt_y"))
                    tilt_removed = wf - tilt_fit
                    pv_tilt, rms_tilt = pv_rms(tilt_removed[mask])
                    power_fit, coeffs = fit_polynomial(
                        wf, mask, terms=("piston", "tilt_x", "tilt_y", "power_x", "power_y")
                    )
                    residual = wf - power_fit
                    irr, residual_rms = pv_rms(residual[mask])
                    score = score_solution(pv_tilt, rms_tilt, irr, radius)
                    row = {
                        "file": path.name,
                        "peak_y": py,
                        "peak_x": px,
                        "radius": radius,
                        "ellipse_ratio": ratio,
                        "pv_after_tilt_waves": pv_tilt,
                        "rms_after_tilt_waves": rms_tilt,
                        "irregularity_after_tilt_power_waves": irr,
                        "residual_rms_waves": residual_rms,
                        "power_x_coeff": float(coeffs.get("power_x", 0.0)),
                        "power_y_coeff": float(coeffs.get("power_y", 0.0)),
                        "score": score,
                    }
                    all_rows.append(row)
                    candidate = (score, row, wf, tilt_removed, residual)
                    if best is None or score < best[0]:
                        best = candidate
                except Exception:
                    continue
    if best is None:
        raise RuntimeError(f"No valid FFT sweep result for {path}")

    _, row, wf, tilt_removed, residual = best
    stem = path.stem
    save_map(OUT_DIR / f"{stem}_best_wavefront.png", wf, f"{stem} best wavefront")
    save_map(OUT_DIR / f"{stem}_best_tilt_removed.png", tilt_removed, f"{stem} best tilt removed")
    save_map(OUT_DIR / f"{stem}_best_residual.png", residual, f"{stem} best residual")

    sweep_path = OUT_DIR / f"{stem}_sweep.csv"
    with sweep_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(all_rows[0]))
        writer.writeheader()
        writer.writerows(sorted(all_rows, key=lambda r: r["score"]))
    return row


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = [analyze_one(path) for path in sorted(ACTIVE_DIR.glob("Zygo*_active.png"))]
    out_csv = OUT_DIR / "improved_fft_best_metrics.csv"
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(out_csv)


if __name__ == "__main__":
    main()
