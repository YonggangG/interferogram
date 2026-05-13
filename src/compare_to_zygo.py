"""Compare first-pass prototype metrics against the Zygo OCR validation manifest."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/raw/zygo_screenshots/validation_manifest.json"
FFT_CSV = ROOT / "reports/initial_fft_analysis/initial_fft_metrics.csv"
OUT = ROOT / "reports/initial_fft_analysis/zygo_comparison.csv"


def rel_error(measured: float, reference: float) -> float | None:
    if reference == 0:
        return None
    return (measured - reference) / reference


def main() -> None:
    manifest = json.loads(MANIFEST.read_text())
    refs = {r["source_file"].split("/")[-1].replace(".png", ""): r for r in manifest["records"]}
    rows = []
    with FFT_CSV.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            stem = Path(row["roi_file"]).name.replace("_fringe_roi.png", "")
            ref = refs[stem]
            measured_pv = float(row["pv_waves_raw"])
            measured_rms = float(row["rms_waves_raw"])
            measured_irr = float(row["irregularity_waves_rect_fit"])
            rows.append({
                "face_id": ref["face_id"],
                "source": stem,
                "zygo_pv_waves": ref["pv_waves"],
                "prototype_pv_waves_raw": measured_pv,
                "pv_rel_error": rel_error(measured_pv, ref["pv_waves"]),
                "zygo_rms_waves": ref["rms_waves"],
                "prototype_rms_waves_raw": measured_rms,
                "rms_rel_error": rel_error(measured_rms, ref["rms_waves"]),
                "zygo_irregularity_waves": ref["irregularity_waves"],
                "prototype_irregularity_waves_rect_fit": measured_irr,
                "irregularity_rel_error": rel_error(measured_irr, ref["irregularity_waves"]),
                "status": "not_matched_first_pass",
            })
    with OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(OUT)


if __name__ == "__main__":
    main()
