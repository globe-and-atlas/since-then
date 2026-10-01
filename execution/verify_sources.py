#!/usr/bin/env python3
"""Check each events.csv row against its cited source; write .tmp/source_report.md.

Wikipedia sources: the page's plain text (MediaWiki API, redirects followed).
DOI sources: the Crossref record (title, year, abstract when deposited).
Every age in the text (Ga/Ma/ka, billion/million/thousand years, BP) is converted to Ma. A row is
MATCH when some stated age lies within its age +/- max(uncertainty, 5%), else CHECK (read by a person).
Responses are cached in .tmp/sources/ so reruns are offline and identical.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
EVENTS = ROOT / "data" / "deep_time" / "events.csv"
CACHE = ROOT / ".tmp" / "sources"
REPORT = ROOT / ".tmp" / "source_report.md"
UA = {"User-Agent": "since-then-source-check/1.0 (Globe & Atlas; github.com/globe-and-atlas)"}

NUM = r"(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)"
UNITS = [
    (rf"{NUM}\s*(?:–|-|to)?\s*(?:\d+(?:\.\d+)?\s*)?(?:billion|bn)\s+years", 1000.0),
    (rf"{NUM}\s*(?:–|-|to)?\s*(?:\d+(?:\.\d+)?\s*)?million\s+years", 1.0),
    (rf"{NUM}\s*(?:–|-|to)?\s*(?:\d+(?:\.\d+)?\s*)?(?:Ga|Gya|Gyr)\b", 1000.0),
    (rf"{NUM}\s*(?:–|-|to)?\s*(?:\d+(?:\.\d+)?\s*)?(?:Ma|Mya|Myr)\b", 1.0),
    (rf"{NUM}\s*(?:–|-|to)?\s*(?:\d+(?:\.\d+)?\s*)?(?:ka|kya)\b", 0.001),
    (rf"{NUM}\s*(?:–|-|to)?\s*(?:\d+(?:\.\d+)?\s*)?thousand\s+years", 0.001),
    (rf"{NUM}\s+years\s+(?:ago|BP|before present|old)", 1e-6),
    (rf"{NUM}\s*(?:BC|BCE)\b", "bce"),
]


def fetch(url: str) -> dict | None:
    try:
        import requests
    except ImportError:
        sys.exit("Missing dependency: pip install requests")
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / (hashlib.sha1(url.encode()).hexdigest() + ".json")
    if path.exists():
        return json.loads(path.read_text())
    for attempt in range(3):
        try:
            r = requests.get(url, headers=UA, timeout=30)
            if r.status_code == 429 and attempt < 2:  # rate limited: wait as asked, then retry
                time.sleep(float(r.headers.get("Retry-After", 10)) + 5)
                continue
            if r.status_code == 404:
                data: dict = {"missing": True}
                break
            r.raise_for_status()
            data = r.json()
            break
        except Exception as exc:  # network: retry, then report
            if attempt == 2:
                return {"error": str(exc)}
            time.sleep(2 * (attempt + 1))
    path.write_text(json.dumps(data))
    time.sleep(1.5)
    return data


def source_text(url: str) -> tuple[str, str]:
    """(status, text) for a source URL."""
    if "wikipedia.org/wiki/" in url:
        title = unquote(url.split("/wiki/", 1)[1])
        api = ("https://en.wikipedia.org/w/api.php?action=query&prop=extracts&explaintext=1"
               f"&redirects=1&format=json&titles={title}")
        data = fetch(api)
        if not data or "error" in data:
            return "ERROR", str(data)
        pages = data.get("query", {}).get("pages", {})
        page = next(iter(pages.values()), {})
        if "missing" in page or not page.get("extract"):
            return "MISSING", ""
        return "OK", page["title"] + "\n" + page["extract"]
    if "doi.org/" in url:
        doi = url.split("doi.org/", 1)[1]
        data = fetch(f"https://api.crossref.org/works/{doi}")
        if not data or data.get("missing") or "error" in data:
            return "MISSING", str(data)
        m = data["message"]
        title = " ".join(m.get("title", []))
        year = (m.get("issued", {}).get("date-parts") or [[None]])[0][0]
        abstract = re.sub(r"<[^>]+>", " ", m.get("abstract", ""))
        return "OK", f"{title} ({m.get('container-title', [''])[0]}, {year})\n{abstract}"
    return "UNSUPPORTED", ""


def ages_in(text: str) -> list[tuple[float, str]]:
    found = []
    for pattern, scale in UNITS:
        for m in re.finditer(pattern, text):
            n = float(m.group(1).replace(",", ""))
            ma = (n + 2000) * 1e-6 if scale == "bce" else n * scale
            lo, hi = max(0, m.start() - 90), min(len(text), m.end() + 60)
            found.append((ma, " ".join(text[lo:hi].split())))
    return found


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true", help="list rows without fetching")
    args = ap.parse_args()
    with EVENTS.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if args.dry_run:
        print(f"{len(rows)} rows to check")
        return
    lines = ["# Source check", "", "| # | age Ma | status | label | source |", "|---|---|---|---|---|"]
    detail = []
    counts: dict[str, int] = {}
    for i, row in enumerate(rows, start=2):
        age, unc = float(row["age_ma"]), float(row["uncertainty_ma"] or 0)
        tol = max(unc, age * 0.05)
        status, text = source_text(row["source"])
        hits = [(a, s) for a, s in ages_in(text) if abs(a - age) <= tol] if status == "OK" else []
        verdict = "MATCH" if hits else ("CHECK" if status == "OK" else status)
        counts[verdict] = counts.get(verdict, 0) + 1
        lines.append(f"| {i} | {row['age_ma']} | {verdict} | {row['label']} | {row['source']} |")
        if verdict != "MATCH":
            near = sorted(ages_in(text), key=lambda h: abs(h[0] - age))[:3]
            head = text.split("\n", 1)[0][:160]
            detail.append(f"## Row {i}: {row['label']} ({row['age_ma']} ± {row['uncertainty_ma']} Ma)\n"
                          f"- source: {row['source']} — {status}; {head}\n"
                          + "".join(f"- nearest: {a:g} Ma — …{s}…\n" for a, s in near))
        else:
            detail.append(f"## Row {i}: MATCH — {row['label']}\n- …{hits[0][1]}…\n")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n\n" + "\n".join(detail))
    print(" ".join(f"{k}={v}" for k, v in sorted(counts.items())), f"-> {REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
