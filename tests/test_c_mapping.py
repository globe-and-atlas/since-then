"""Validation contract: the Python mapping and the C mapping agree to the second at 100 sampled times.

Compiles deep_age() (and its helper thousands()) straight out of watchface/src/c/main.c with the host C
compiler, so the test exercises the watch's own integer maths rather than a port of it.
"""
from __future__ import annotations

import importlib.util
import random
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
MAIN_C = ROOT / "watchface" / "src" / "c" / "main.c"
_spec = importlib.util.spec_from_file_location("build_deep_time", ROOT / "execution" / "build_deep_time.py")
bdt = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bdt)

CC = shutil.which("cc") or shutil.which("clang") or shutil.which("gcc")
EARTH_YEARS = int(bdt.EARTH_MA * 1_000_000)


def c_function(source: str, name: str) -> str:
    """The text of a top-level `static ... name(...) { ... }` definition, braces balanced."""
    m = re.search(rf"^static [^\n]*\b{name}\(", source, re.M)
    assert m, f"{name} not found in main.c"
    depth, i = 0, source.index("{", m.start())
    while True:
        depth += {"{": 1, "}": -1}.get(source[i], 0)
        i += 1
        if depth == 0:
            return source[m.start():i]


def sample_times() -> list[int]:
    """100 clock seconds: the anchors, both ends of the day, the last minute and a fixed random spread."""
    fixed = [0, 1, 40725, 76146, 85143, 86340, 86394, 86398, 86399, 43200]
    rng = random.Random(4540)
    return fixed + rng.sample(range(86400), 100 - len(fixed))


@pytest.fixture(scope="module")
def c_ages(tmp_path_factory: pytest.TempPathFactory) -> dict[int, tuple[str, str]]:
    if CC is None:
        pytest.skip("no host C compiler")
    src = MAIN_C.read_text()
    harness = "\n".join([
        "#include <stdio.h>", "#include <stdint.h>", "#include <string.h>", "#include <stddef.h>",
        re.search(r"^#define DAY .*$", src, re.M).group(0),
        re.search(r"^#define EARTH_YEARS .*$", src, re.M).group(0),
        c_function(src, "thousands"),
        c_function(src, "deep_age"),
        "int main(void) { int t; char num[24]; const char *unit;",
        "  while (scanf(\"%d\", &t) == 1) { deep_age(t, num, sizeof(num), &unit); printf(\"%d|%s|%s\\n\", t, num, unit); }",
        "  return 0; }",
    ])
    work = tmp_path_factory.mktemp("cmap")
    (work / "h.c").write_text(harness)
    exe = work / "h"
    subprocess.run([CC, "-std=c99", "-Wall", "-Werror", "-o", str(exe), str(work / "h.c")], check=True)
    out = subprocess.run([str(exe)], input="\n".join(map(str, sample_times())), capture_output=True, text=True, check=True)
    return {int(t): (num, unit) for t, num, unit in (line.split("|") for line in out.stdout.splitlines())}


def parse_years(num: str, unit: str) -> float:
    value = float(num.replace(",", ""))
    return value * {"billion years ago": 1e9, "million years ago": 1e6, "years ago": 1}[unit]


def test_c_covers_every_sample(c_ages: dict[int, tuple[str, str]]) -> None:
    assert sorted(c_ages) == sorted(sample_times())


@pytest.mark.parametrize("t", sample_times())
def test_c_and_python_agree_to_the_second(c_ages: dict[int, tuple[str, str]], t: int) -> None:
    num, unit = c_ages[t]
    shown = parse_years(num, unit)
    expected = bdt.age_at(t) * 1_000_000
    # The C value is truncated for display (0.01 Ga; 0.1 Ma below 10 Ma, whole Ma above; whole years).
    step = {"billion years ago": 1e7, "million years ago": 1e5 if expected < 1e7 else 1e6, "years ago": 1}[unit]
    assert expected - step < shown <= expected + 1e-6, f"t={t}: C shows {num} {unit}, Python {expected:,.0f} years"
    # Back on the clock, the age C shows lands within the second Python assigns it to.
    exact = EARTH_YEARS * (86400 - t) // 86400
    if unit == "years ago":
        assert int(shown) == exact
        assert int(86400 * (1 - shown / EARTH_YEARS)) in (t, t - 1)
