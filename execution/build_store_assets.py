#!/usr/bin/env python3
"""Build the RePebble store assets for Since Then from the screenshot tour.

Input: .tmp/store_tour/NN.png from `python3 execution/capture_store_tour.py` (TOUR order in main.c).
Output, in prod/appstore/ (store screenshot names must start with the platform, "emery_"):
  emery_01_second_millennium_day.gif   animated, Second Millennium only: 1001 CE to now across the day
  emery_02..13_*.png                   three stills for each timeline: Second Millennium, Deep Time,
                                       Holocene, Common Era
  icons/thumbnail-80.png, icons/thumbnail-144.png   the full screen on a black square
Usage: python3 execution/build_store_assets.py [--dry-run]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOUR = ROOT / ".tmp" / "store_tour"
OUT = ROOT / "prod" / "appstore"
SCREEN = (200, 228)
GIF_FRAMES = range(0, 13)  # tour stops 00..12: Second Millennium, 01:00 to 23:45
FRAME_MS = 1100
LAST_FRAME_MS = 2600       # linger on the present before the loop restarts
STILLS = {
    "emery_02_second_millennium_0700.png": 3,
    "emery_03_second_millennium_1500.png": 7,
    "emery_04_second_millennium_2230.png": 11,
    "emery_05_deep_time_1119.png": 13,
    "emery_06_deep_time_2340.png": 14,
    "emery_07_deep_time_235950.png": 15,
    "emery_08_holocene_0300.png": 16,
    "emery_09_holocene_1200.png": 17,
    "emery_10_holocene_2130.png": 18,
    "emery_11_common_era_0600.png": 19,
    "emery_12_common_era_1200.png": 20,
    "emery_13_common_era_2200.png": 21,
}
GIF_NAME = "emery_01_second_millennium_day.gif"
ICON_STOP = 14  # Deep Time 23:40, unchanged
ICON_SIZES = (80, 144)


def load(stop: int):
    from PIL import Image
    path = TOUR / f"{stop:02d}.png"
    if not path.exists():
        sys.exit(f"missing {path.relative_to(ROOT)}: run execution/capture_store_tour.py first")
    img = Image.open(path).convert("RGB")
    if img.size != SCREEN:
        sys.exit(f"{path.name} is {img.size}, expected {SCREEN}")
    return img


def icon(img, size: int):
    from PIL import Image
    canvas = Image.new("RGB", (size, size), "black")
    w = round(SCREEN[0] * size / SCREEN[1])  # fit the full height so no label is cropped
    canvas.paste(img.resize((w, size), Image.LANCZOS), ((size - w) // 2, 0))
    return canvas


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="check inputs and list outputs without writing")
    args = ap.parse_args()
    try:
        from PIL import Image
    except ImportError:
        sys.exit("Missing dependency: pip install pillow")
    frames = [load(i) for i in GIF_FRAMES]
    stills = {name: load(stop) for name, stop in STILLS.items()}
    source = load(ICON_STOP)
    outputs = [GIF_NAME, *STILLS, *(f"icons/thumbnail-{s}.png" for s in ICON_SIZES)]
    if args.dry_run:
        print("would write:", ", ".join(outputs))
        return
    (OUT / "icons").mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("emery_*"):  # names change between tours; never upload a stale screenshot
        old.unlink()
    pal = [f.convert("P", palette=Image.ADAPTIVE, colors=64) for f in frames]  # the screen has 64 colours
    durations = [FRAME_MS] * (len(pal) - 1) + [LAST_FRAME_MS]
    pal[0].save(OUT / GIF_NAME, save_all=True, append_images=pal[1:], duration=durations, loop=0, optimize=False)
    for name, img in stills.items():
        img.save(OUT / name)
    for s in ICON_SIZES:
        icon(source, s).save(OUT / "icons" / f"thumbnail-{s}.png")
    print("wrote", len(outputs), "files to", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
