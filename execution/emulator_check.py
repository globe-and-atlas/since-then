#!/usr/bin/env python3
"""Emulator checks for the Since Then watchface (Pebble Time 2 / emery). Screenshots: .tmp/emulator/.

Pinned scenarios build with ST_TEST_SECONDS and ST_TEST_LENS:
  deep_1119     Deep Time 11:19      Paleoproterozoic unit, oxygen event
  deep_2339     Deep Time 23:39:30   Cretaceous–Paleogene boundary
  deep_235950   Deep Time 23:59:50   seconds shown, age under 600,000 years
  holocene_1200 / ce_1200 / m2_1200  each historical lens at noon
  bluetooth     Deep Time 11:19 with Bluetooth disconnected: identical to deep_1119
  settings      noon, lens from settings: Setting_Lens "2" (string, as Clay sends a select) then 3 (int),
                sent by numeric key (send-app-message takes no names)
Running-clock scenario (ST_TEST_START_MINUTE=1438, real seconds; emu-set-time is reset to host time):
  midnight      starts 23:58; logs must show "tick: seconds" at 23:59, then "tick: minutes" after 00:00

Pixel checks are coarse (band drawn, event text present); every screenshot is kept for review.
Usage: python3 execution/emulator_check.py [--only NAME ...] [--dry-run]
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FACE = ROOT / "watchface"
OUT = ROOT / ".tmp" / "emulator"
BAND = (0, 70, 200, 92)
EVENT = (6, 116, 194, 156)

PINNED = {
    "deep_1119": (0, 11 * 3600 + 19 * 60),
    "deep_2339": (0, 23 * 3600 + 39 * 60 + 30),
    "deep_235950": (0, 86390),
    "holocene_1200": (1, 43200),
    "ce_1200": (2, 43200),
    "m2_1200": (3, 43200),
}


def run(cmd: list[str], timeout: int = 300, env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=FACE, capture_output=True, text=True, timeout=timeout, env=env)


def build(lens: int | None = None, seconds: int | None = None, start_minute: int | None = None) -> None:
    env = {k: v for k, v in os.environ.items() if not k.startswith("ST_TEST_")}
    if start_minute is not None:
        env["ST_TEST_START_MINUTE"] = str(start_minute)
    if lens is not None:
        env["ST_TEST_LENS"] = str(lens)
    if seconds is not None:
        env["ST_TEST_SECONDS"] = str(seconds)
    run(["pebble", "clean"], timeout=60)
    r = run(["pebble", "build"], env=env)
    if r.returncode:
        raise SystemExit("build failed:\n" + r.stdout[-2000:] + r.stderr[-2000:])


def install() -> None:
    r = run(["pebble", "install", "--emulator", "emery"], timeout=300)
    if "succeeded" not in r.stdout + r.stderr:
        raise SystemExit("install failed:\n" + r.stdout[-2000:] + r.stderr[-2000:])
    time.sleep(3)


def shot(name: str):
    from PIL import Image
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{name}.png"
    run(["pebble", "screenshot", "--emulator", "emery", "--no-open", str(path)], timeout=60)
    return Image.open(path).convert("RGB")


def share(img, box, test) -> float:
    pixels = list(img.crop(box).get_flattened_data())
    return sum(1 for p in pixels if test(p)) / len(pixels)


def check(results: list[tuple[str, bool]], name: str, ok: bool) -> None:
    results.append((name, ok))
    print(f"{'PASS' if ok else 'FAIL'}  {name}")


def pinned(name: str, results: list[tuple[str, bool]]) -> None:
    lens, seconds = PINNED[name]
    build(lens, seconds)
    install()
    img = shot(name)
    check(results, f"{name}: band drawn", share(img, BAND, lambda p: p != (0, 0, 0)) > 0.8)
    check(results, f"{name}: event text", share(img, EVENT, lambda p: p == (255, 255, 255)) > 0.02)


def bluetooth(results: list[tuple[str, bool]]) -> None:
    build(*PINNED["deep_1119"])
    install()
    before = shot("bluetooth_on")
    run(["pebble", "emu-bt-connection", "--emulator", "emery", "--connected", "no"], timeout=60)
    time.sleep(3)
    after = shot("bluetooth_off")
    run(["pebble", "emu-bt-connection", "--emulator", "emery", "--connected", "yes"], timeout=60)
    body = (0, 30, 200, 228)  # the status icon area may change; the face below it must not
    check(results, "bluetooth: face unchanged", list(before.crop(body).get_flattened_data()) == list(after.crop(body).get_flattened_data()))


def settings(results: list[tuple[str, bool]]) -> None:
    build(seconds=43200)  # lens not pinned: it comes from persist / the settings message
    install()
    import json
    uuid = json.loads((FACE / "package.json").read_text())["pebble"]["uuid"]
    key = json.loads((FACE / "build" / "js" / "message_keys.json").read_text())["Setting_Lens"]
    send = ["pebble", "send-app-message", "--emulator", "emery", "--app-uuid", uuid]
    run(send + ["--int", f"{key}=0"], timeout=60)
    time.sleep(2)
    deep = shot("settings_deep")
    run(send + ["--string", f"{key}=2"], timeout=60)
    time.sleep(2)
    ce = shot("settings_ce")
    run(send + ["--int", f"{key}=3"], timeout=60)
    time.sleep(2)
    m2 = shot("settings_2m")
    run(send + ["--int", f"{key}=0"], timeout=60)
    age = (0, 30, 200, 66)
    differ = lambda a, b: list(a.crop(age).get_flattened_data()) != list(b.crop(age).get_flattened_data())
    check(results, "settings: string lens switches the face", differ(deep, ce))
    check(results, "settings: int lens switches the face", differ(ce, m2))


def midnight(results: list[tuple[str, bool]]) -> None:
    build(lens=0, start_minute=1438)
    logs = subprocess.Popen(["pebble", "install", "--emulator", "emery", "--logs"], cwd=FACE,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    try:
        start = time.time()
        time.sleep(75)  # past the first real minute boundary: the face is in 23:59
        shot("midnight_before")
        time.sleep(max(0, 140 - (time.time() - start)))  # past the second: after midnight
        shot("midnight_after")
    finally:
        logs.terminate()
    text = logs.communicate(timeout=10)[0]
    (OUT / "midnight_logs.txt").write_text(text)
    seconds_at = text.find("tick: seconds")
    check(results, "midnight: seconds in the last minute", seconds_at >= 0)
    check(results, "midnight: minutes after midnight", text.find("tick: minutes", seconds_at + 1) > seconds_at >= 0)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    names = [*PINNED, "bluetooth", "settings", "midnight"]
    ap.add_argument("--only", nargs="*", choices=names)
    ap.add_argument("--dry-run", action="store_true", help="list scenarios and exit")
    args = ap.parse_args()
    chosen = args.only or names
    if args.dry_run:
        print("scenarios:", " ".join(chosen))
        return
    try:
        import PIL  # noqa: F401
    except ImportError:
        sys.exit("Missing dependency: pip install pillow")
    results: list[tuple[str, bool]] = []
    for name in chosen:
        if name in PINNED:
            pinned(name, results)
        elif name == "bluetooth":
            bluetooth(results)
        elif name == "settings":
            settings(results)
        else:
            midnight(results)
    build()  # leave a clean, unpinned build behind
    print(f"{sum(ok for _, ok in results)}/{len(results)} passed; screenshots: {OUT.relative_to(ROOT)}")
    sys.exit(0 if all(ok for _, ok in results) else 1)


if __name__ == "__main__":
    main()
