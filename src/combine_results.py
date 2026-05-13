"""Combine FFT and display-map analysis routes for the six Zygo screenshots."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/raw/zygo_screenshots/validation_manifest.json"
FFT = ROOT / "reports/improved_fft_sweep/improved_fft_zygo_comparison.csv"
DISPLAY = ROOT / "reports/display_wavefront_analysis/display_wavefront_metrics.csv"
OUT = ROOT / "reports/combined_route_comparison.csv"


def read_csv_by_face(path: Path) -> dict[str, dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return {r["face_id"]: r for r in csv.DictReader(f)}


def main() -> None:
    refs = {r["face_id"]: r for r in json.loads(MANIFEST.read_text())["records"]}
    fft = read_csv_by_face(FFT)
    display = read_csv_by_face(DISPLAY)
    rows = []
    for face_id, ref in refs.items():
        f = fft[face_id]
        d = display[face_id]
        fft_rms_err = abs(float(f["rms_rel_error"]))
        disp_rms_err = abs(float(d["rms_rel_error"]))
        rows.append(
            {
                "face_id": face_id,
                "zygo_pv_waves": ref["pv_waves"],
                "zygo_rms_waves": ref["rms_waves"],
                "zygo_irregularity_waves": ref["irregularity_waves"],
                "fft_pv_after_tilt_waves": f["prototype_pv_after_tilt_waves"],
                "fft_rms_after_tilt_waves": f["prototype_rms_after_tilt_waves"],
                "fft_irregularity_waves": f["prototype_irregularity_after_tilt_power_waves"],
                "fft_irregularity_rel_error": f["irregularity_rel_error"],
                "display_rms_waves": d["display_calibrated_rms_waves"],
                "display_rms_rel_error": d["rms_rel_error"],
                "preferred_current_route_for_screenshot_validation": "display_map" if disp_rms_err < fft_rms_err else "fft_fringe",
                "note": "Display route uses Zygo PV calibration; FFT route is independent from fringe patch but still not matched.",
            }
        )
    with OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(OUT)


if __name__ == "__main__":
    main()
