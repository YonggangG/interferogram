"""Command-line entrypoints for iflat."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .display_wavefront import analyze_zygo_display_screenshot
from .raw_fringe import analyze_raw_fringe


def _bbox(value: str) -> list[int]:
    parts = [int(float(p.strip())) for p in value.split(",")]
    if len(parts) != 4:
        raise argparse.ArgumentTypeError("bbox must be x1,y1,x2,y2")
    return parts


def main() -> None:
    parser = argparse.ArgumentParser(prog="iflat")
    sub = parser.add_subparsers(dest="cmd", required=True)

    raw = sub.add_parser("raw-fringe", help="Analyze a direct fringe image")
    raw.add_argument("image")
    raw.add_argument("--out", default="reports/cli_raw_fringe")
    raw.add_argument("--bbox", type=_bbox)
    raw.add_argument("--wavelength-nm", type=float, default=633.0)

    zygo = sub.add_parser("zygo-screenshot", help="Audit a Zygo screenshot display map")
    zygo.add_argument("image")
    zygo.add_argument("--out", default="reports/cli_zygo_screenshot")
    zygo.add_argument("--map-bbox", type=_bbox, required=True)
    zygo.add_argument("--colorbar-bbox", type=_bbox, required=True)
    zygo.add_argument("--pv-waves", type=float, required=True)
    zygo.add_argument("--wavelength-nm", type=float, default=633.0)

    args = parser.parse_args()
    if args.cmd == "raw-fringe":
        result = analyze_raw_fringe(args.image, Path(args.out), bbox=args.bbox, wavelength_nm=args.wavelength_nm)
    else:
        result = analyze_zygo_display_screenshot(
            args.image,
            Path(args.out),
            map_bbox=args.map_bbox,
            colorbar_bbox=args.colorbar_bbox,
            calibration_pv_waves=args.pv_waves,
            wavelength_nm=args.wavelength_nm,
        )
    print(json.dumps(asdict(result), indent=2))


if __name__ == "__main__":
    main()
