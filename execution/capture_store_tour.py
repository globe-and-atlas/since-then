#!/usr/bin/env python3
"""Capture the store screenshot tour from the emulator into .tmp/store_tour/NN.png.

Builds the face with ST_TEST_TOUR=1 (main.c TOUR: Deep Time across the day, then three stills each for
Holocene, Common Era and Second Millennium), installs it once, and taps through: each `pebble emu-tap`
moves the face to the next stop. Ends with a clean, unpinned release build.
Usage: python3 execution/capture_store_tour.py [--dry-run]
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FACE = ROOT / "watchface"
OUT = ROOT / ".tmp" / "store_tour"


def tour_count() -> int:
    src = (FACE / "src" / "c" / "main.c").read_text()
    table = src[src.index("TOUR[] = {"):src.index("};", src.index("TOUR[] = {"))]
    return len(re.findall(r"\{\d+, \d+\}", table))


def pebble(*args: str, env: dict | None = None, timeout: int = 240) -> subprocess.CompletedProcess:
    return subprocess.run(["pebble", *args], cwd=FACE, capture_output=True, text=True, timeout=timeout, env=env)


def build(tour: bool) -> None:
    env = {k: v for k, v in os.environ.items() if not k.startswith("ST_TEST_")}
    if tour:
        env["ST_TEST_TOUR"] = "1"
    pebble("clean")
    r = pebble("build", env=env)
    if r.returncode:
        sys.exit("build failed:\n" + r.stdout[-1500:] + r.stderr[-1500:])


def shot(path: Path) -> None:
    path.unlink(missing_ok=True)
    for _ in range(3):
        pebble("screenshot", "--emulator", "emery", "--no-open", str(path), timeout=60)
        if path.exists():
            return
        time.sleep(3)
    sys.exit(f"screenshot failed: {path.name}")


def on_screen() -> bool:
    """Since Then is showing: its unit band (y 70..92) is solid colour, which no other face draws there."""
    from PIL import Image
    probe = OUT / "probe.png"
    shot(probe)
    img = Image.open(probe).convert("RGB")
    band = img.crop((0, 70, 200, 92)).getdata()
    # The corner check rejects the grey "X is not responding" screen, whose band area is also filled.
    return img.getpixel((198, 226)) == (0, 0, 0) and sum(1 for px in band if px != (0, 0, 0)) / len(band) > 0.8


def launch() -> None:
    """Install until Since Then is on screen: installs on a fresh or long-running emulator often lose the switch."""
    for _ in range(3):
        pebble("kill")
        time.sleep(3)
        pebble("install", "--emulator", "emery")  # boots the emulator
        time.sleep(10)
        pebble("install", "--emulator", "emery")
        time.sleep(10)
        if on_screen():
            return
    sys.exit("Since Then never came on screen")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="report the tour length and exit")
    args = ap.parse_args()
    n = tour_count()
    if args.dry_run:
        print(f"tour: {n} stops -> {OUT.relative_to(ROOT)}/00..{n - 1:02d}.png")
        return
    OUT.mkdir(parents=True, exist_ok=True)
    try:
        build(tour=True)
        launch()
        for i in range(n):
            if i:
                pebble("emu-tap", "--emulator", "emery", timeout=60)
                time.sleep(2.5)
            shot(OUT / f"{i:02d}.png")
            print(f"stop {i:02d}")
    finally:
        build(tour=False)
    print(f"{n} screenshots in {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
