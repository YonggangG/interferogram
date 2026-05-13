"""Run first-pass FFT phase extraction on prepared Zygo fringe ROI crops."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from fourier_phase import extract_phase_fft
from mask_utils import aperture_mask
from metrics import compute_metrics


ROOT = Path(__file__).resolve().parents[1]
ROI_DIR = ROOT / "data/processed/fringe_roi"
OUT_DIR = ROOT / "reports/initial_fft_analysis"


def read_gray(path: Path) -> np.ndarray:
    return np.asarray(Image.open(path).convert("L"), dtype=float)


def save_map(path: Path, arr: np.ndarray, title: str, cmap: str = "RdBu_r") -> None:
    plt.figure(figsize=(5, 4))
    plt.imshow(arr, cmap=cmap)
    plt.colorbar(label="waves")
    plt.title(title)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for roi_path in sorted(ROI_DIR.glob("Zygo*_fringe_roi.png")):
        gray = read_gray(roi_path)
        mask = aperture_mask(gray)
        result = extract_phase_fft(gray, mask=mask)
        # Remove arbitrary piston before reporting raw PV/RMS. The absolute phase offset is arbitrary.
        wf = result.wavefront_waves - np.nanmean(result.wavefront_waves[mask])
        metrics = compute_metrics(wf, mask=mask)

        stem = roi_path.stem
        np.save(OUT_DIR / f"{stem}_wavefront_waves.npy", wf)
        save_map(OUT_DIR / f"{stem}_wavefront_waves.png", np.where(mask, wf, np.nan), f"{stem} wavefront")
        save_map(OUT_DIR / f"{stem}_wrapped_phase.png", np.where(mask, result.wrapped_phase, np.nan), f"{stem} wrapped phase", cmap="twilight")
        plt.imsave(OUT_DIR / f"{stem}_mask.png", mask, cmap="gray")

        row = {
            "roi_file": str(roi_path.relative_to(ROOT)),
            "carrier_peak_y": result.carrier_peak[0],
            "carrier_peak_x": result.carrier_peak[1],
            "filter_radius_px": result.filter_radius_px,
            "pv_waves_raw": metrics.pv,
            "rms_waves_raw": metrics.rms,
            "power_x_coeff": metrics.power_x,
            "power_y_coeff": metrics.power_y,
            "power_mean_coeff": metrics.power_mean,
            "irregularity_waves_rect_fit": metrics.irregularity,
            "mask_valid_pixels": int(mask.sum()),
        }
        row.update({f"coef_{k}": v for k, v in metrics.coefficients.items()})
        rows.append(row)

    csv_path = OUT_DIR / "initial_fft_metrics.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=sorted(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (OUT_DIR / "initial_fft_metrics.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(csv_path)


if __name__ == "__main__":
    main()
