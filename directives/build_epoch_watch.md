---
generated_by: "Claude Code CLI (claude-opus-5-5)"
timestamp: "2026-09-29T21:10:00-05:00"
---

# Build Since Then

## Goal
**Since Then** (tagline: "All in a day"; repo `epoch-watch`) is a Pebble Time 2 (Emery, 200×228, 64 colours) watchface that squeezes a span of time into one day. Midnight is the start of the span, the next midnight is the present, and the face shows where on that span the current moment falls: the geological period (or historical age) and the nearest event. It's a Globe & Atlas project and a sibling of From Here, with one idea you can read at a glance.

Lens 1 is **Deep Time**: Earth's history (4,540 million years) stretched over 24 hours.
- 1 minute ≈ 3.15 million years; 1 second ≈ 52,500 years.
- Oxygen fills the air mid-morning, animals appear after 21:00, and the dinosaurs die at 23:39.
- Homo sapiens arrives at 23:59:54, so the whole of human history fits in the last six seconds.

Design decisions (user, 2026-09-29):
- **Time-based lenses only.** Narrative lenses (the Odyssey, the Hero's Journey, film arcs) are out of scope.
- **Deep Time ships alone first.** More lenses come in Phase 2, and only after the gate below is passed.
- Emery only, like From Here.

## Mapping
- The clock time t, in seconds since local midnight (0 ≤ t < 86,400), maps to an age:
  `age_Ma = 4540 × (1 − t / 86400)`
- The scale is linear. A log scale would lose the "humans in the last seconds" payoff, which is the point.
- 00:00 is Earth's formation, 4,540 ± 50 Ma (Dalrymple 2001) (owner decision, 2026-09-29). It is a constant in one place.
- The ICS Hadean base (4,567.3 Ma, the Solar System) is older than 00:00, so the Hadean is clipped to start at 00:00.

Anchor times, all derived from the formula and used in the tests:

| Event | Age | Clock |
|---|---|---|
| Great Oxidation Event begins | ~2,400 Ma | ~11:19 |
| Base of the Cambrian | 538.8 Ma | ~21:09 |
| End-Cretaceous extinction | 66.0 Ma | ~23:39 |
| Homo sapiens | ~300 ka | 23:59:54 |

## Architecture
**No phone and no network.** All data is compiled into the watch as a resource, so the whole class of AppMessage failures that hit From Here on hardware (2026-09-29) can't happen. There is no `src/pkjs` in version 1.

- **Data** (`data/deep_time/`, hand-curated CSVs checked into git):
  - `units.csv`: the ICS chronostratigraphic units.
    - Columns: eon, era, period and epoch names; base age in Ma; the ICS chart colour as hex.
    - Source: ICS International Chronostratigraphic Chart (cite the version).
  - `events.csv`: events.
    - Columns: `age_ma`, `uncertainty_ma`, `label` (≤ 2 lines at GOTHIC_18), `source` (a URL or citation).
    - The wording is our own; facts are not copyrightable, but sentences are.
- **Build** (`execution/build_deep_time.py`, deterministic):
  - Validates both CSVs (see the contract).
  - Converts ages to clock seconds.
  - Picks the ICS colour nearest in the Pebble 64-colour palette.
  - Writes `watchface/resources/deep_time.bin`: a sorted, fixed-width record table the C code binary-searches.
- **Watch** (`watchface/src/c/`):
  - Time bar: the clock time, then the equivalent age ("312 Ma ago", "4.1 Ga ago", "48,000 years ago").
  - Unit band: the current period, or the era or eon where no period is defined (Hadean, Archean, most of the Proterozoic), drawn in its ICS colour.
  - Event panel: the latest event at or before now, with how long ago it happened on the watch's clock ("12 min ago").
  - Strip: a 24-hour bar coloured by eon, with a cursor at now.
  - Ticks every minute. From 23:59:00 it ticks every second so the last minute plays out, then returns to minute ticks after midnight.

## Tools

| Script | Purpose |
|---|---|
| `execution/fetch_ics_units.py` | Fetch the ICS chart (pinned commit, CC BY 4.0) and write `units.csv` |
| `execution/build_deep_time.py` | Validate CSVs, convert ages to clock seconds, write `deep_time.bin` |
| `execution/emulator_check.py` | Emulator screenshots at the anchor times (`pebble emu-set-time`) with pixel checks |
| `execution/cloudpebble.py` | Simulate a CloudPebble GitHub import (copy from `from-here`) |

## Validation Contract (2026-09-29)
Mapping:
- [ ] t = 0 maps to 4,540 Ma (unit test).
- [ ] t = 86,399 maps to under 0.06 Ma (unit test).
- [ ] 66.0 Ma maps to 23:39 ± 1 min (unit test).
- [ ] 538.8 Ma maps to 21:09 ± 1 min (unit test).
- [ ] 0.3 Ma maps to 23:59:54 ± 1 s (unit test).
- [ ] The Python mapping and the C mapping agree to the second at 100 sampled times (test compiles or ports the C formula).

Data:
- [ ] Every row of `events.csv` has a non-empty `source`.
- [ ] Every row of `units.csv` cites the ICS chart version.
- [ ] Every event age lies in [0, 4540] Ma.
- [ ] Unit base ages strictly decrease within each rank.
- [ ] Every clock minute from 00:00 to 23:58 falls inside a unit (no uncovered minute).
- [ ] No gap between consecutive events exceeds 30 clock minutes.
- [ ] The final clock minute (23:59) holds at least 3 events.
- [ ] Every label fits two lines at GOTHIC_18 within 188 px (checked by the build against a width table).
- [ ] `deep_time.bin` is under 24 KB.
- [ ] The build is deterministic: two runs produce byte-identical `deep_time.bin`.

Watch:
- [ ] `pebble build` succeeds for Emery with no warnings in our sources.
- [ ] At 11:19 the emulator shows a Paleoproterozoic unit and an oxygen event (screenshot inspected).
- [ ] At 23:39 it shows the Cretaceous–Paleogene boundary (screenshot inspected).
- [ ] At 23:59:50 it shows seconds ticking and an age under 600,000 years (screenshot inspected).
- [ ] At 00:00:30 it has returned to minute ticks (tick-unit log line in `pebble logs`).
- [ ] Every age label uses the right unit: Ga ≥ 1,000 Ma, Ma ≥ 1 Ma, otherwise years with thousands separators.
- [ ] With Bluetooth disconnected (`pebble emu-bt-connection --connected no`) the face is unchanged.

Process:
- [ ] `pytest` passes.
- [ ] The emulator checks pass.
- [ ] The CloudPebble simulation drops no files.
- [ ] A fresh verifier approves.
- [ ] A day on the physical watch confirms it's readable at a glance. Battery drain is logged in SESSION.md.

## Phase 2: historical lenses (gated)
**Gate:** Deep Time has run on the owner's wrist for 7 days and still earns glances. The owner decides. Only then add a lens setting (the first `src/pkjs` and Clay page) and these lenses:

| Lens | Span | Scale | Note |
|---|---|---|---|
| Holocene | 11,700 years before 2000 CE → today | ≈ 8.1 years/min | ICS Holocene base (b2k) |
| Common Era | 1 CE → today | ≈ 1.4 years/min | There is no year 0 |
| Second Millennium | 1001 CE → today | ≈ 0.71 years/min | |

- "Today" comes from the watch's date, so these spans grow slowly. Deep Time's doesn't need to.
- Each lens gets its own CSV, the same validation, and a contract appended here with its own anchor times, written before its code.
- A historical lens needs about 1 event per 10 minutes and no region dominating. Record the regional balance per lens in `knowledge/domain/`.

## Outputs
| Artifact | Location | Notes |
|---|---|---|
| Curated data | `data/deep_time/units.csv`, `events.csv` | In git, with a source on every row |
| Watch resource | `watchface/resources/deep_time.bin` | Built; commit it so CloudPebble imports work |
| Watchface | `watchface/` | CloudPebble-importable layout |
| PBW | `watchface/build/watchface.pbw` | Gitignored |

## Edge cases
- DST days: the clock is local time. A 23- or 25-hour day skips or repeats an hour of Earth history, which is acceptable and should be noted in the README.
- Ages with large uncertainty: show "~" when `uncertainty_ma / age_ma > 0.05`.
- Precambrian stretches with no periods: the unit band shows the era, or the eon where no era is defined.
- 12-hour clock setting: the face stays 24-hour on purpose, because midnight-to-midnight is the span. Say so in the README.

## Open questions (owner)
1. ~~Name~~ Resolved 2026-09-29: **Since Then**. No Pebble store title uses it (checked against the store's search). "Deep Time" is crowded outside Pebble (DeepTime for Geology, Deep Time Walk). The name fits every lens, and "deep time" goes in the store description for search.
2. ~~00:00 anchor~~ Resolved 2026-09-29: Earth's formation, 4,540 Ma.

## Learnings — 2026-09-29 (data slice)
- **Units come from the ICS chart's own RDF** (`i-c-stratigraphy/chart`, pinned commit `81618a8`, "Modified 2024-12", CC BY 4.0): 74 units with base, uncertainty and official colour. It has newer values than older summaries: the Cretaceous base is 143.1 ± 0.6 Ma, not 145.
- **The 30-minute gap rule bites in the Precambrian.** 30 clock minutes is 94.6 Myr, so the familiar round 100 Myr steps fail. The gaps were filled with more real events, not by moving ages.
- **`events.csv` gained a `kind` column** (`event` or `state`). A few rows describe conditions (no free oxygen, a fainter Sun, closer Moon) and sit inside their true range with a wide uncertainty.
- **The last second is crowded.** Four events are younger than one clock second (52,546 years): Out of Africa, the LGM, the Holocene and writing. All share 23:59:59 or 23:59:58, so the watch can show only the latest. Open design question: rotate them within the final second, or show a "last second" list.
- **The label width check is approximate** (a conservative per-character table for GOTHIC_18). The emulator screenshot is the real check.
- **Results:** 74 units, 110 events, `deep_time.bin` 9,818 bytes, deterministic; pytest 21 passed.

## Historical lenses — 2026-09-30 (owner decision: build now)
The owner overrode the 7-day wrist gate on 2026-09-30: the Holocene, Common Era and Second Millennium lenses ship with Deep Time.

**Data model.**
- One file, `data/history/events.csv`: `year` (historical, no year 0, negative = BC), `uncertainty_years`, `kind`, `region`, `label`, `source`.
- Each lens takes the events inside its span. The Second Millennium is a subset of the Common Era, which is a subset of the Holocene.

| Lens | Start | 30 clock min ≈ |
|---|---|---|
| Holocene | 9700 BC (astronomical −9699; 11,700 years before 2000 CE) | 244 years |
| Common Era | 1 CE | 42 years |
| Second Millennium | 1001 CE | 21 years |

**Mapping.**
- The span is [start, now], where now is the watch's fractional current year.
- `year(t) = start + (now − start) × t / 86400`.
- The watch converts each event's year to a clock time itself, so the face never goes stale as years pass.

**Watch.**
- A lens setting (the first `src/pkjs` and Clay page) picks Deep Time, Holocene, Common Era or Second Millennium.
- Holocene band: the ICS Holocene ages (Greenlandian to 6236 BC, Northgrippian to 2250 BC, Meghalayan), computed in C.
- Common Era and Second Millennium band: the century ("12th century").
- Approximate events show "c." before the year.

**Tools.**

| Script | Purpose |
|---|---|
| `execution/build_history.py` | Validate `data/history/events.csv` per lens and write `watchface/resources/history.bin` |
| `execution/verify_sources.py --data history` | Check each row's year against its cited source |

**Validation contract (historical lenses):**
- [ ] No row has year 0 (unit test).
- [ ] 9700 BC maps to 00:00 in the Holocene lens (unit test).
- [ ] 1013 CE maps to 12:00 ± 1 min in the Common Era lens (reference present 2026) (unit test).
- [ ] 1513 CE maps to 12:00 ± 1 min in the Second Millennium lens (unit test).
- [ ] The present maps to 24:00 in every lens (unit test).
- [ ] Every row has an https source.
- [ ] Every row has a region from: Global, Africa, Americas, Asia, Europe, Middle East, Oceania.
- [ ] In each lens, no gap between consecutive events (or between an end and the nearest event) exceeds 30 clock minutes at the reference present.
- [ ] In each lens, no single region holds more than 40% of the events.
- [ ] In each lens, Africa, Americas, Asia, Europe and the Middle East each have at least 3 events.
- [ ] In each lens, Oceania has at least 2 events.
- [ ] Every label fits two lines (same width check as Deep Time).
- [ ] `history.bin` is under 24 KB.
- [ ] The build is deterministic: two runs give byte-identical output.
- [ ] Every row's year is confirmed against its source by `verify_sources.py --data history`, or by a hand verdict recorded in `knowledge/domain/history_sources.md`.
- [ ] Each rule test also rejects a deliberately broken dataset (Popper's shield).
- [ ] The emulator shows each lens at 12:00 with a plausible year and event (screenshots inspected).
- [ ] Switching the lens in settings changes the face within one minute (emulator).

## Learnings — 2026-09-30 (historical data)
- **Wikipedia's millennium pages (10th to 1st millennium BC) are good sources** for prehistoric dates. Each page states "c. N BC" for its events, so the source check can confirm the dates directly.
- **The Second Millennium's 21-year gap rule is the tightest.** The 11th–13th centuries needed extra events (Canossa 1077, Kaifeng 1127, Saladin 1169, the Mamluks 1250).
- **Result:** 228 events. Holocene 228, Common Era 134, Second Millennium 96. Europe is at most 26% of any lens. `history.bin` is 15,578 bytes. pytest 38 passed.
