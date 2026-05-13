"""Extract displayed Zygo wavefront-map and colorbar crops from screenshots.

Bounding boxes are vision-assisted bootstrap coordinates for the first six
validation screenshots. Later versions should auto-detect the plot area.
"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "data/raw/zygo_screenshots"
OUT_DIR = ROOT / "data/processed/zygo_wavefront_display"

BBOXES = {
    "Zygo0": {"map": [122, 136, 748, 710], "colorbar": [900, 66, 927, 804]},
    "Zygo1": {"map": [153, 133, 710, 671], "colorbar": [844, 58, 868, 731]},
    "Zygo2": {"map": [130, 121, 718, 679], "colorbar": [846, 62, 884, 763]},
    "Zygo3": {"map": [158, 124, 666, 668], "colorbar": [778, 42, 843, 729]},
    "Zygo4": {"map": [110, 97, 560, 543], "colorbar": [652, 31, 710, 615]},
    "Zygo5": {"map": [156, 119, 647, 653], "colorbar": [758, 42, 824, 713]},
}


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    metadata = []
    for screenshot in sorted(SRC_DIR.glob("Zygo*.png")):
        stem = screenshot.stem
        boxes = BBOXES[stem]
        image = Image.open(screenshot).convert("RGB")
        map_crop = image.crop(boxes["map"])
        colorbar_crop = image.crop(boxes["colorbar"])
        map_file = OUT_DIR / f"{stem}_wavefront_display.png"
        colorbar_file = OUT_DIR / f"{stem}_colorbar.png"
        map_crop.save(map_file)
        colorbar_crop.save(colorbar_file)
        metadata.append(
            {
                "source": str(screenshot.relative_to(ROOT)),
                "map_file": str(map_file.relative_to(ROOT)),
                "colorbar_file": str(colorbar_file.relative_to(ROOT)),
                "map_bbox": boxes["map"],
                "colorbar_bbox": boxes["colorbar"],
                "method": "vision_assisted_manual_bootstrap",
            }
        )
    (OUT_DIR / "wavefront_display_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(OUT_DIR / "wavefront_display_metadata.json")


if __name__ == "__main__":
    main()
