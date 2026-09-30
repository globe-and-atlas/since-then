#!/usr/bin/env python3
"""Fetch the ICS International Chronostratigraphic Chart (CC BY 4.0) and write data/deep_time/units.csv.

The chart is pinned to one commit of github.com/i-c-stratigraphy/chart so reruns are identical.
Units older than Earth's formation (00:00 on the face) keep their ICS base; the build clips them.
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "deep_time" / "units.csv"
CACHE = ROOT / ".tmp" / "chart.ttl"
COMMIT = "81618a865cdb04998355a302f3e859908a080c0e"  # 2026-07-27; chart "Modified 2024-12"
URL = f"https://raw.githubusercontent.com/i-c-stratigraphy/chart/{COMMIT}/chart.ttl"
SOURCE = (
    "ICS International Chronostratigraphic Chart v2024-12 (Cohen, Harper, Gibbard & Car 2025, "
    f"Episodes 48:105-115), CC BY 4.0, i-c-stratigraphy/chart@{COMMIT[:7]}"
)
RANKS = ["Eon", "Era", "Period", "Epoch"]
FIELDS = ["rank", "name", "parent", "base_ma", "base_uncertainty_ma", "top_ma", "color", "source"]


def download() -> Path:
    try:
        import requests
    except ImportError:
        sys.exit("Missing dependency: pip install requests")
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    if not CACHE.exists():
        r = requests.get(URL, timeout=60)
        r.raise_for_status()
        CACHE.write_bytes(r.content)
    return CACHE


def parse(path: Path) -> list[dict[str, str]]:
    try:
        from rdflib import BNode, Graph, Namespace, URIRef
        from rdflib.namespace import SKOS
    except ImportError:
        sys.exit("Missing dependency: pip install rdflib")
    g = Graph()
    g.parse(path, format="turtle")
    GTS = Namespace("http://resource.geosciml.org/ontology/timescale/gts#")
    RANK = Namespace("http://resource.geosciml.org/ontology/timescale/rank/")
    GTSD = Namespace("https://data.stratigraphy.org/data/gts/")
    TIME = Namespace("http://www.w3.org/2006/time#")
    SCHEMA = Namespace("https://schema.org/")

    def label(node: URIRef) -> str:
        for o in g.objects(node, SKOS.prefLabel):
            if getattr(o, "language", None) == "en":
                return str(o)
        return str(node).rsplit("/", 1)[-1]

    def boundary(node: URIRef, pred: URIRef) -> tuple[float | None, float | None]:
        for b in g.objects(node, pred):
            if isinstance(b, BNode):
                age = g.value(b, GTSD.inMYA)
                err = g.value(b, SCHEMA.marginOfError)
                return (float(age) if age is not None else None, float(err) if err is not None else None)
        return (None, None)

    rows = []
    for rank in RANKS:
        for node in g.subjects(GTS.rank, RANK[rank]):
            base, base_err = boundary(node, TIME.hasBeginning)
            top, _ = boundary(node, TIME.hasEnd)
            color = g.value(node, SCHEMA.color)
            parent = g.value(node, SKOS.broader)
            if base is None or top is None:
                continue
            rows.append({
                "rank": rank.lower(),
                "name": label(node),
                "parent": label(parent) if parent is not None else "",
                "base_ma": f"{base:g}",
                "base_uncertainty_ma": f"{base_err:g}" if base_err is not None else "",
                "top_ma": f"{top:g}",
                "color": str(color).upper() if color is not None else "",
                "source": SOURCE,
            })
    rows.sort(key=lambda r: (RANKS.index(r["rank"].title()), -float(r["base_ma"])))
    return rows


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true", help="parse and report without writing")
    args = ap.parse_args()
    rows = parse(download())
    counts = {r: sum(1 for x in rows if x["rank"] == r.lower()) for r in RANKS}
    print(f"{len(rows)} units: {counts}")
    if args.dry_run:
        return
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
