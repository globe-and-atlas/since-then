"""Validation contract (directives/build_epoch_watch.md): Mapping and Data sections."""
from __future__ import annotations

import copy
import importlib.util
import struct
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("build_deep_time", ROOT / "execution" / "build_deep_time.py")
bdt = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bdt)

UNITS = bdt.read_csv(bdt.DATA / "units.csv")
EVENTS = bdt.read_csv(bdt.DATA / "events.csv")


def hms(h: int, m: int, s: int = 0) -> int:
    return h * 3600 + m * 60 + s


# ---------------- mapping ----------------

def test_midnight_is_earth_formation() -> None:
    assert bdt.age_at(0) == 4540.0


def test_last_second_is_nearly_now() -> None:
    assert bdt.age_at(86399) < 0.06


@pytest.mark.parametrize("age, clock, tol", [
    (66.0, hms(23, 39), 60),
    (538.8, hms(21, 9), 60),
    (2400, hms(11, 19), 60),
    (0.3, hms(23, 59, 54), 1),
])
def test_anchor_times(age: float, clock: int, tol: int) -> None:
    assert abs(bdt.clock_s(age) - clock) <= tol


def test_clock_is_floor_and_clipped() -> None:
    assert bdt.clock_s(4567) == 0  # ICS Hadean base is older than 00:00
    assert bdt.clock_s(0) == 86399
    assert bdt.clock_s(bdt.age_at(1000.5)) == 1000


# ---------------- data ----------------

def test_data_passes_validation() -> None:
    assert bdt.validate(UNITS, EVENTS) == []


def test_every_event_has_a_source() -> None:
    assert all(e["source"].startswith("https://") for e in EVENTS)


def test_every_event_has_a_kind() -> None:
    assert {e["kind"] for e in EVENTS} <= {"event", "state"}


def test_last_minute_holds_three_events() -> None:
    assert sum(1 for e in EVENTS if bdt.clock_s(float(e["age_ma"])) >= 86340) >= 3


# Popper's shield: each rule must actually reject a broken dataset.

def test_rejects_missing_source() -> None:
    events = copy.deepcopy(EVENTS)
    events[5]["source"] = ""
    assert any("no source" in e for e in bdt.validate(UNITS, events))


def test_rejects_large_gap() -> None:
    events = [e for e in EVENTS if not 1000 < float(e["age_ma"]) < 1300]
    assert any("over 30 min" in e for e in bdt.validate(UNITS, events))


def test_rejects_long_label() -> None:
    events = copy.deepcopy(EVENTS)
    events[0]["label"] = "Earth forms from the swirling disc of dust and gas around the very young Sun, slowly"
    assert any("more than 2 lines" in e for e in bdt.validate(UNITS, events))


def test_rejects_age_out_of_range() -> None:
    events = copy.deepcopy(EVENTS)
    events[0]["age_ma"] = "4600"
    assert any("outside" in e for e in bdt.validate(UNITS, events))


def test_rejects_uncited_unit() -> None:
    units = copy.deepcopy(UNITS)
    units[0]["source"] = "memory"
    assert any("ICS" in e for e in bdt.validate(units, EVENTS))


# ---------------- resource ----------------

def test_resource_is_small_and_deterministic() -> None:
    a, b = bdt.pack(UNITS, EVENTS), bdt.pack(UNITS, EVENTS)
    assert a == b
    assert len(a) < 24 * 1024


def test_resource_layout() -> None:
    blob = bdt.pack(UNITS, EVENTS)
    assert blob[:4] == b"STN1"
    units, events = struct.unpack_from("<HH", blob, 4)
    assert (units, events) == (len(UNITS), len(EVENTS))
    unit_size = 4 + 4 + 1 + 1 + bdt.UNIT_NAME
    event_size = 4 + 1 + bdt.EVENT_LABEL
    assert len(blob) == 8 + units * unit_size + events * event_size
    first = 8 + units * unit_size
    times = [struct.unpack_from("<I", blob, first + i * event_size)[0] for i in range(events)]
    assert times == sorted(times)


def test_committed_resource_matches_data() -> None:
    assert bdt.OUT.read_bytes() == bdt.pack(UNITS, EVENTS), "run execution/build_deep_time.py"


def test_gcolor8_extremes() -> None:
    assert bdt.gcolor8("#000000") == 0xC0
    assert bdt.gcolor8("#FFFFFF") == 0xFF
    assert bdt.gcolor8("#7FC64E") == 0xC0 | (1 << 4) | (2 << 2) | 1
