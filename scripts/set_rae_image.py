#!/usr/bin/env python3
"""Install your own photograph as the Rose theme's optional tile.

    venv/bin/python scripts/set_rae_image.py /path/to/pet.png

Takes any image, keeps transparency, trims the empty space around the subject
so the subject sits in the middle of the tile, and writes it where the theme expects.
"""

import sys
from pathlib import Path

from PIL import Image

TARGET = Path(__file__).resolve().parent.parent / "dashboard" / "icons" / "rae.png"
TILE = 300


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    source = Path(sys.argv[1]).expanduser()
    if not source.is_file():
        print(f"No such image: {source}", file=sys.stderr)
        return 2

    img = Image.open(source).convert("RGBA")
    # Trim the transparent margin, so the tile spacing is about the subject and not
    # about however much empty space the cut-out happened to leave.
    box = img.getbbox()
    if box:
        img = img.crop(box)

    img.thumbnail((TILE, TILE), Image.LANCZOS)
    canvas = Image.new("RGBA", (TILE, TILE), (0, 0, 0, 0))
    canvas.paste(img, ((TILE - img.width) // 2, (TILE - img.height) // 2), img)

    TARGET.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(TARGET)
    print(f"Installed {source.name} -> {TARGET}")
    print(f"  {img.width}x{img.height} on a {TILE}x{TILE} tile"
          f"{'' if img.mode == 'RGBA' else ' (no transparency in the source)'}")
    print("Reload the app and choose the Rose theme.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
