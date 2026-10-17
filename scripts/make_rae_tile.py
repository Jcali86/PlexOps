#!/usr/bin/env python3
"""Draw a pet backdrop with hearts and monkey toys from your own cutout.

The skin lays this down as a repeating tile at nine percent, so everything
here reads as texture rather than picture - which is why the toys and hearts
are solid shapes rather than drawings with detail that would be thrown away.

Every motif is also drawn at the tile's opposite edges, so the pattern joins
itself and no seam shows where the tile repeats.

    venv/bin/python scripts/make_rae_tile.py /path/to/pet-cutout.png
"""

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "dashboard/icons/rae.png"

TILE = 560
PINK = (255, 143, 177, 255)
DEEP = (235, 117, 154, 255)
SOFT = (255, 194, 214, 255)


def wrapped(base, sprite, x, y):
    """Paste so that anything crossing an edge appears on the opposite one."""
    for dx in (-TILE, 0, TILE):
        for dy in (-TILE, 0, TILE):
            base.alpha_composite(sprite, (x + dx, y + dy))


def heart(size, colour):
    """A heart, drawn big and flat because nine percent eats fine detail."""
    s = size * 4                      # oversample, then shrink: smoother edges
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r = s * 0.27
    d.ellipse([s * 0.5 - r * 2, s * 0.18, s * 0.5, s * 0.18 + r * 2], fill=colour)
    d.ellipse([s * 0.5, s * 0.18, s * 0.5 + r * 2, s * 0.18 + r * 2], fill=colour)
    d.polygon([(s * 0.5 - r * 1.94, s * 0.44), (s * 0.5 + r * 1.94, s * 0.44),
               (s * 0.5, s * 0.9)], fill=colour)
    return img.resize((size, size), Image.LANCZOS)


def monkey(size, colour):
    """A plush monkey: head, ears, long arms, curl of a tail."""
    s = size * 4
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = s * 0.5

    # arms, thrown wide the way a soft toy hangs
    d.line([(s * 0.30, s * 0.52), (s * 0.10, s * 0.36)], fill=colour,
           width=int(s * 0.09), joint="curve")
    d.line([(s * 0.70, s * 0.52), (s * 0.90, s * 0.36)], fill=colour,
           width=int(s * 0.09), joint="curve")
    for hx in (s * 0.10, s * 0.90):
        d.ellipse([hx - s * 0.06, s * 0.30, hx + s * 0.06, s * 0.42], fill=colour)

    # legs
    d.line([(s * 0.40, s * 0.74), (s * 0.32, s * 0.90)], fill=colour,
           width=int(s * 0.09), joint="curve")
    d.line([(s * 0.60, s * 0.74), (s * 0.68, s * 0.90)], fill=colour,
           width=int(s * 0.09), joint="curve")

    # tail
    d.arc([s * 0.58, s * 0.62, s * 0.96, s * 0.98], start=250, end=60,
          fill=colour, width=int(s * 0.055))

    d.ellipse([cx - s * 0.20, s * 0.44, cx + s * 0.20, s * 0.80], fill=colour)  # body
    for ex in (cx - s * 0.22, cx + s * 0.22):                                   # ears
        d.ellipse([ex - s * 0.10, s * 0.16, ex + s * 0.10, s * 0.36], fill=colour)
    d.ellipse([cx - s * 0.19, s * 0.12, cx + s * 0.19, s * 0.50], fill=colour)  # head
    return img.resize((size, size), Image.LANCZOS)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="your own pet cutout image")
    source = parser.parse_args().source.expanduser()
    if not source.is_file():
        raise SystemExit(f"Cannot find {source}")

    rae = Image.open(source).convert("RGBA")
    rae = rae.crop(rae.getbbox())              # drop the empty margins
    scale = (TILE * 0.46) / rae.height
    rae = rae.resize((round(rae.width * scale), round(rae.height * scale)), Image.LANCZOS)

    tile = Image.new("RGBA", (TILE, TILE), (0, 0, 0, 0))

    # Two of her, set on a diagonal so the repeat does not read as rows.
    wrapped(tile, rae, int(TILE * 0.04), int(TILE * 0.03))
    wrapped(tile, rae, int(TILE * 0.54), int(TILE * 0.53))

    hearts = [(0.62, 0.06, 74, PINK), (0.86, 0.22, 46, SOFT), (0.72, 0.36, 34, DEEP),
              (0.05, 0.56, 52, SOFT), (0.30, 0.44, 38, PINK), (0.44, 0.88, 60, PINK),
              (0.90, 0.70, 40, DEEP), (0.16, 0.92, 34, SOFT), (0.98, 0.94, 48, PINK)]
    for fx, fy, size, colour in hearts:
        sprite = heart(size, colour).rotate(((fx + fy) * 180) % 40 - 20,
                                            resample=Image.BICUBIC, expand=True)
        wrapped(tile, sprite, int(TILE * fx), int(TILE * fy))

    monkeys = [(0.80, 0.02, 92, SOFT), (0.02, 0.30, 78, PINK),
               (0.46, 0.62, 70, SOFT), (0.66, 0.84, 84, PINK)]
    for fx, fy, size, colour in monkeys:
        sprite = monkey(size, colour).rotate(((fx * 7 + fy * 3) * 120) % 30 - 15,
                                             resample=Image.BICUBIC, expand=True)
        wrapped(tile, sprite, int(TILE * fx), int(TILE * fy))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    tile.save(OUT, optimize=True)
    print(f"  {OUT.relative_to(ROOT)}  {tile.width}x{tile.height}  "
          f"{OUT.stat().st_size:,d} bytes")


if __name__ == "__main__":
    main()
