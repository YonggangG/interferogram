"""Compare active-aperture FFT analysis against Zygo references."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/raw/zygo_screenshots/validation_manifest.json"
METRICS = ROOT / "reports/active_fft_analysis/active_fft_metrics.csv"
OUT = ROOT / "reports/active_fft_analysis/active_fft_zygo_comparison.csv"


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
                    "zygo_rms_waves": ref["rms_waves"],
                    "prototype_rms_after_tilt_waves": rms,
                    "zygo_irregularity_waves": ref["irregularity_waves"],
                    "prototype_irregularity_after_tilt_power_waves": irr,
                    "irregularity_rel_error": (irr - ref["irregularity_waves"]) / ref["irregularity_waves"],
                    "selected_radius": row["selected_radius"],
                    "status": "second_pass_active_aperture_not_final",
                }
            )
    with OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(OUT)


if __name__ == "__main__":
    main()
