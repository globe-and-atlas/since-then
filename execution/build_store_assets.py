#!/usr/bin/env python3
"""Build the RePebble store assets for Since Then from the emulator screenshots.

Input: .tmp/emulator/*.png from `python3 execution/emulator_check.py` (pinned times, 200x228 emery).
Output, in prod/appstore/:
  emery_1_lenses.gif       animated: the four timelines you can choose, one after another
  emery_2_deep_1119.png    Deep Time 11:19, the Great Oxidation Event
  emery_3_deep_2340.png    Deep Time 23:40, just after the dinosaurs die
  emery_4_deep_235950.png  Deep Time 23:59:50, the last minute in seconds
  emery_5_holocene.png     Holocene at noon
  icons/thumbnail-80.png, icons/thumbnail-144.png   the full screen on a black square
Store screenshot filenames must start with the platform name ("emery_").
Usage: python3 execution/build_store_assets.py [--dry-run]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOTS = ROOT / ".tmp" / "emulator"
OUT = ROOT / "prod" / "appstore"
SCREEN = (200, 228)
# One frame per lens, in the order the settings page lists them.
LENSES = ["deep_2340", "holocene_1200", "ce_1200", "m2_1200"]
FRAME_MS = 1800
STILLS = {
    "emery_2_deep_1119.png": "deep_1119",
    "emery_3_deep_2340.png": "deep_2340",
    "emery_4_deep_235950.png": "deep_235950",
    "emery_5_holocene.png": "holocene_1200",
}
ICON_SOURCE = "deep_2340"
ICON_SIZES = (80, 144)


def load(name: str):
    from PIL import Image
    path = SHOTS / f"{name}.png"
    if not path.exists():
        sys.exit(f"missing {path.relative_to(ROOT)}: run execution/emulator_check.py first")
    img = Image.open(path).convert("RGB")
    if img.size != SCREEN:
        sys.exit(f"{path.name} is {img.size}, expected {SCREEN}")
    return img


def icon(img, size: int):
    from PIL import Image
    canvas = Image.new("RGB", (size, size), "black")
    scale = size / SCREEN[1]  # fit the full height so no label is cropped
    w, h = round(SCREEN[0] * scale), size
    canvas.paste(img.resize((w, h), Image.LANCZOS), ((size - w) // 2, 0))
    return canvas


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="check inputs and list outputs without writing")
    args = ap.parse_args()
    try:
        from PIL import Image
    except ImportError:
        sys.exit("Missing dependency: pip install pillow")
    frames = [load(n) for n in LENSES]
    stills = {out: load(src) for out, src in STILLS.items()}
    source = load(ICON_SOURCE)
    outputs = ["emery_1_lenses.gif", *STILLS, *(f"icons/thumbnail-{s}.png" for s in ICON_SIZES)]
    if args.dry_run:
        print("would write:", ", ".join(outputs))
        return
    (OUT / "icons").mkdir(parents=True, exist_ok=True)
    # The emery screen is 64 colours, so an adaptive palette loses nothing.
    pal = [f.convert("P", palette=Image.ADAPTIVE, colors=64) for f in frames]
    pal[0].save(OUT / "emery_1_lenses.gif", save_all=True, append_images=pal[1:], duration=FRAME_MS, loop=0, optimize=False)
    for out, img in stills.items():
        img.save(OUT / out)
    for s in ICON_SIZES:
        icon(source, s).save(OUT / "icons" / f"thumbnail-{s}.png")
    print("wrote", ", ".join(outputs), "to", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
