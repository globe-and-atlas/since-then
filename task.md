# Task: Since Then (epoch-watch)

## Objective

Build the Deep Time watchface for Pebble Time 2: Earth's 4,540-million-year history stretched over one day, fully offline. Directive: `directives/build_epoch_watch.md` (full validation contract).

## Next
- [x] `data/deep_time/units.csv` holds the ICS units, citing the chart version.
- [x] `data/deep_time/events.csv` meets the coverage rules (no gap over 30 clock minutes; at least 3 events in 23:59).
- [x] Every `events.csv` row is checked against its cited source (87 automatically, 23 by hand: `knowledge/domain/deep_time_sources.md`).
- [x] `execution/build_deep_time.py` passes the Data section of the contract.
- [x] Decide how the final second shows the 4 events that share 23:59:58-59 (they take turns every 333 ms).
- [x] `watchface/` builds for Emery.
- [x] The emulator checks pass at the anchor times (17/17).
- [x] The CloudPebble simulation drops no files.
- [x] A fresh verifier approves (2026-10-01, second pass; the first pass rejected d6d61e7, see knowledge/ERRORS.md).
- [ ] A day on the physical watch: legible at a glance; battery drain logged.

## Historical lenses (owner: build now, 2026-09-30)
- [x] `data/history/events.csv` passes `execution/build_history.py` for all three lenses.
- [x] Every history row is confirmed against its source (226 automatically, 2 by hand: `knowledge/domain/history_sources.md`).
- [x] The lens setting (Clay page) switches the face (string and int, emulator).

## Parked
- Narrative lenses: scrapped 2026-09-29.
