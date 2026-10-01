"""Validation contract (directives/build_epoch_watch.md): historical lenses."""
from __future__ import annotations

import copy
import importlib.util
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "execution"))
_spec = importlib.util.spec_from_file_location("build_history", ROOT / "execution" / "build_history.py")
bh = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bh)

EVENTS = bh.read_csv()
LENS = dict(bh.LENSES)


# ---------------- mapping ----------------

def test_no_year_zero() -> None:
    assert bh.astro(-1) == 0 and bh.astro(1) == 1
    assert all(int(e["year"]) != 0 for e in EVENTS)


@pytest.mark.parametrize("lens, year, minute", [
    ("Common Era", 1, 0),
    ("Common Era", 1013, 720),        # halfway through 1..2026 is about 1013
    ("Second Millennium", 1001, 0),
    ("Second Millennium", 1513, 720),
    ("Holocene", -9700, 0),           # 9700 BC is astronomical -9699
])
def test_lens_anchor_minutes(lens: str, year: int, minute: float) -> None:
    assert abs(bh.clock_min(year, LENS[lens]) - minute) <= 1


def test_present_is_midnight() -> None:
    for start in LENS.values():
        assert bh.clock_min(2026, start) == pytest.approx(1440)


def test_holocene_start_is_ics_base() -> None:
    assert 2000 - bh.astro(-9700) == 11700 - 1  # 11,700 years before 2000 CE, counted astronomically


# ---------------- data ----------------

def test_data_passes_validation() -> None:
    assert bh.validate(EVENTS) == []


def test_every_lens_has_events_at_each_end() -> None:
    for name, start in bh.LENSES:
        times = sorted(bh.clock_min(int(e["year"]), start) for e in bh.in_lens(EVENTS, start))
        assert times[0] <= bh.MAX_GAP_MIN and times[-1] >= 1440 - bh.MAX_GAP_MIN, name


# Popper's shield: each rule must reject a broken dataset.

def test_rejects_gap() -> None:
    events = [e for e in EVENTS if not 1300 < int(e["year"]) < 1400]
    assert any("Second Millennium: gap" in e for e in bh.validate(events))


def test_rejects_region_imbalance() -> None:
    events = copy.deepcopy(EVENTS)
    for e in events:
        if 1001 <= int(e["year"]) and e["region"] != "Oceania":
            e["region"] = "Europe"
    assert any("Second Millennium: Europe" in e for e in bh.validate(events))


def test_rejects_missing_region() -> None:
    events = [e for e in EVENTS if not (int(e["year"]) > 1000 and e["region"] == "Oceania")]
    assert any("Oceania has" in e for e in bh.validate(events))


def test_rejects_year_zero() -> None:
    events = copy.deepcopy(EVENTS)
    events[0]["year"] = "0"
    assert any("year 0" in e for e in bh.validate(events))


def test_rejects_unknown_region() -> None:
    events = copy.deepcopy(EVENTS)
    events[0]["region"] = "Atlantis"
    assert any("unknown region" in e for e in bh.validate(events))


# ---------------- resource ----------------

def test_resource_layout_and_determinism() -> None:
    blob = bh.pack(EVENTS)
    assert blob == bh.pack(EVENTS) and len(blob) < bh.MAX_BYTES
    assert blob[:4] == b"HST1"
    lenses, events = struct.unpack_from("<HH", blob, 4)
    assert (lenses, events) == (len(bh.LENSES), len(EVENTS))
    lens_size, event_size = 2 + bh.LENS_NAME, 2 + 1 + 1 + bh.EVENT_LABEL
    assert len(blob) == 8 + lenses * lens_size + events * event_size
    first = 8 + lenses * lens_size
    years = [struct.unpack_from("<h", blob, first + i * event_size)[0] for i in range(events)]
    assert years == sorted(years)


def test_committed_resource_matches_data() -> None:
    assert bh.OUT.read_text() == bh.c_header(bh.pack(EVENTS), "HISTORY_DATA", "execution/build_history.py"), "run execution/build_history.py"
