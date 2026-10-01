#!/usr/bin/env python3
"""Validate data/history/events.csv for the historical lenses; write watchface/resources/history.bin.

Each lens squeezes [start, now] into one day: 00:00 is the start year and 24:00 is the present.
"Now" moves, so the watch maps years to clock time itself; this script only checks the data against
a reference present (REF_NOW) and packs it.

Years are historical (no year 0; negative = BC). Astronomical year = year if year > 0 else year + 1.

history.bin (little-endian):
  header  "HST1", u16 lens_count, u16 event_count
  lens    i16 start (astronomical year), char name[LENS_NAME]
  event   i16 year (historical), u8 flags (1 = approximate), u8 region, char label[EVENT_LABEL]
Events are sorted by year.
"""
from __future__ import annotations

import argparse
import csv
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_deep_time import EVENT_LABEL, wrap_lines  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "history" / "events.csv"
OUT = ROOT / "watchface" / "resources" / "history.bin"

REF_NOW = 2026.0  # validation reference; the watch uses the real date
LENS_NAME = 20
LENSES = [  # (name, start as astronomical year)
    ("Holocene", -9699),  # 9700 BC: 11,700 years before 2000 CE (ICS Holocene base)
    ("Common Era", 1),
    ("Second Millennium", 1001),
]
REGIONS = ["Global", "Africa", "Americas", "Asia", "Europe", "Middle East", "Oceania"]
MIN_PER_REGION = {"Africa": 3, "Americas": 3, "Asia": 3, "Europe": 3, "Middle East": 3, "Oceania": 2}
MAX_REGION_SHARE = 0.40
MAX_GAP_MIN = 30
MAX_BYTES = 24 * 1024


def astro(year: int) -> int:
    return year if year > 0 else year + 1


def clock_min(year: int, start: int, now: float = REF_NOW) -> float:
    return 1440 * (astro(year) - start) / (now - start)


def read_csv(path: Path = DATA) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def in_lens(events: list[dict[str, str]], start: int, now: float = REF_NOW) -> list[dict[str, str]]:
    return [e for e in events if start <= astro(int(e["year"])) <= now]


def validate(events: list[dict[str, str]], now: float = REF_NOW) -> list[str]:
    errors: list[str] = []
    for i, e in enumerate(events, start=2):
        if not e["source"].startswith("https://"):
            errors.append(f"events.csv:{i} has no source")
        if int(e["year"]) == 0:
            errors.append(f"events.csv:{i} year 0 does not exist")
        if e["region"] not in REGIONS:
            errors.append(f"events.csv:{i} unknown region {e['region']!r}")
        if e["kind"] not in ("event", "state"):
            errors.append(f"events.csv:{i} unknown kind {e['kind']!r}")
        if len(wrap_lines(e["label"])) > 2:
            errors.append(f"events.csv:{i} label needs more than 2 lines: {e['label']!r}")
        if len(e["label"].encode("utf-8")) >= EVENT_LABEL:
            errors.append(f"events.csv:{i} label over {EVENT_LABEL - 1} bytes")
    for name, start in LENSES:
        lens = in_lens(events, start, now)
        times = sorted(clock_min(int(e["year"]), start, now) for e in lens)
        if not times:
            errors.append(f"{name}: no events")
            continue
        edges = [0.0, *times, 1440.0]
        for a, b in zip(edges, edges[1:]):
            if b - a > MAX_GAP_MIN:
                errors.append(f"{name}: gap {int(a) // 60:02d}:{int(a) % 60:02d} to {int(b) // 60:02d}:{int(b) % 60:02d} over {MAX_GAP_MIN} min")
        counts = {r: sum(1 for e in lens if e["region"] == r) for r in REGIONS}
        for region, n in counts.items():
            if region != "Global" and n / len(lens) > MAX_REGION_SHARE:
                errors.append(f"{name}: {region} is {n}/{len(lens)} events, over {MAX_REGION_SHARE:.0%}")
        for region, least in MIN_PER_REGION.items():
            if counts[region] < least:
                errors.append(f"{name}: {region} has {counts[region]} events, needs {least}")
    return errors


def pack(events: list[dict[str, str]]) -> bytes:
    def fixed(s: str, n: int) -> bytes:
        return s.encode("utf-8").ljust(n, b"\0")

    rows = sorted(events, key=lambda e: int(e["year"]))
    out = bytearray(b"HST1") + struct.pack("<HH", len(LENSES), len(rows))
    for name, start in LENSES:
        out += struct.pack("<h", start) + fixed(name, LENS_NAME)
    for e in rows:
        flags = 1 if int(e["uncertainty_years"] or 0) > 0 else 0
        out += struct.pack("<hBB", int(e["year"]), flags, REGIONS.index(e["region"])) + fixed(e["label"], EVENT_LABEL)
    return bytes(out)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="validate only; write nothing")
    args = ap.parse_args()
    events = read_csv()
    errors = validate(events)
    for e in errors:
        print(f"ERROR {e}", file=sys.stderr)
    if errors:
        sys.exit(1)
    blob = pack(events)
    if len(blob) > MAX_BYTES:
        sys.exit(f"ERROR history.bin is {len(blob)} bytes, over {MAX_BYTES}")
    for name, start in LENSES:
        lens = in_lens(events, start)
        regions = ", ".join(f"{r} {sum(1 for e in lens if e['region'] == r)}" for r in REGIONS)
        print(f"{name}: {len(lens)} events ({regions})")
    print(f"{len(events)} events, {len(blob)} bytes")
    if args.dry_run:
        return
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(blob)
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
