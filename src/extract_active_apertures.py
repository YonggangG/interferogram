"""Extract active fringe apertures from the already-cropped Zygo fringe panels.

The current bounding boxes are manually/vision-assisted from the initial six
validation screenshots. They are intentionally stored here as bootstrap data;
automatic active-aperture detection will replace this after more examples.
"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ROI_DIR = ROOT / "data/processed/fringe_roi"
OUT_DIR = ROOT / "data/processed/fringe_active_aperture"

ACTIVE_BBOXES = {
    "Zygo0_fringe_roi": [119, 164, 229, 267],
    "Zygo1_fringe_roi": [116, 151, 223, 247],
    "Zygo2_fringe_roi": [109, 156, 219, 255],
    "Zygo3_fringe_roi": [116, 148, 220, 242],
    "Zygo4_fringe_roi": [98, 126, 188, 201],
    "Zygo5_fringe_roi": [114, 143, 212, 236],
}


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    metadata = []
    for roi_path in sorted(ROI_DIR.glob("Zygo*_fringe_roi.png")):
        bbox = ACTIVE_BBOXES[roi_path.stem]
        active = Image.open(roi_path).convert("RGB").crop(bbox)
        out_path = OUT_DIR / f"{roi_path.stem}_active.png"
        active.save(out_path)
        metadata.append(
            {
                "source_roi": str(roi_path.relative_to(ROOT)),
                "active_file": str(out_path.relative_to(ROOT)),
                "bbox_in_roi": bbox,
                "active_size": list(active.size),
                "method": "vision_assisted_manual_bootstrap",
            }
        )
    (OUT_DIR / "active_aperture_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(OUT_DIR / "active_aperture_metadata.json")


if __name__ == "__main__":
    main()
