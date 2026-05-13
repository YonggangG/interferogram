"""Compare improved FFT sweep best results against Zygo references."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/raw/zygo_screenshots/validation_manifest.json"
METRICS = ROOT / "reports/improved_fft_sweep/improved_fft_best_metrics.csv"
OUT = ROOT / "reports/improved_fft_sweep/improved_fft_zygo_comparison.csv"


def main() -> None:
    refs = json.loads(MANIFEST.read_text())["records"]
    rows = []
    with METRICS.open(newline="", encoding="utf-8") as f:
        for ref, row in zip(refs, csv.DictReader(f), strict=True):
            pv = float(row["pv_after_tilt_waves"])
            rms = float(row["rms_after_tilt_waves"])
            irr = float(row["irregularity_after_tilt_power_waves"])
            rows.append(
                {
                    "face_id": ref["face_id"],
                    "zygo_pv_waves": ref["pv_waves"],
                    "prototype_pv_after_tilt_waves": pv,
                    "pv_rel_error": (pv - ref["pv_waves"]) / ref["pv_waves"],
                    "zygo_rms_waves": ref["rms_waves"],
                    "prototype_rms_after_tilt_waves": rms,
                    "rms_rel_error": (rms - ref["rms_waves"]) / ref["rms_waves"],
                    "zygo_irregularity_waves": ref["irregularity_waves"],
                    "prototype_irregularity_after_tilt_power_waves": irr,
                    "irregularity_rel_error": (irr - ref["irregularity_waves"]) / ref["irregularity_waves"],
                    "peak_y": row["peak_y"],
                    "peak_x": row["peak_x"],
                    "radius": row["radius"],
                    "ellipse_ratio": row["ellipse_ratio"],
                    "status": "improved_fft_sweep_not_final",
                }
            )
    with OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(OUT)


if __name__ == "__main__":
    main()
