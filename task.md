# Task: Since Then (epoch-watch)

## Objective

Build the Deep Time watchface for Pebble Time 2: Earth's 4,540-million-year history stretched over one day, fully offline. Directive: `directives/build_epoch_watch.md` (full validation contract).

## Next
- [x] `data/deep_time/units.csv` holds the ICS units, citing the chart version.
- [x] `data/deep_time/events.csv` meets the coverage rules (no gap over 30 clock minutes; at least 3 events in 23:59).
- [x] Every `events.csv` row is checked against its cited source (87 automatically, 23 by hand: `knowledge/domain/deep_time_sources.md`).
- [x] `execution/build_deep_time.py` passes the Data section of the contract.
- [ ] Decide how the final second shows the 4 events that share 23:59:58-59.
- [ ] `watchface/` builds for Emery.
- [ ] The emulator checks pass at the anchor times.

## Parked
- Phase 2 lenses (Holocene, Common Era, Second Millennium): after the 7-day wrist gate.
- Narrative lenses: scrapped 2026-09-29.
