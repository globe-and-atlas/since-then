# Errors

Record deterministic errors, root causes, and fixes here.

## 2026-09-30: event sources written from memory
- **A wrong DOI and a non-existent page** in `events.csv` (1630 Ma and 385 Ma), plus two pages that didn't support their dates. Cause: sources were attached from memory, not looked up. Fix: `execution/verify_sources.py` fetches every source and checks the stated ages. Hand-checked rows are recorded in `domain/deep_time_sources.md`. Graduated rule: run the verifier before committing any `events.csv` change.
- **Wikipedia API rate limit (HTTP 429)** at about one request per 0.3 s. The script now waits 1.5 s and honours Retry-After.

## 2026-10-01: verifier rejection of the watchface (d6d61e7)
- **Run-together epoch names on the face** ("UpperCretaceous"). Cause: the ICS chart has no English label for 20 epochs, and `fetch_ics_units.py` fell back to the URI slug. Fix: split the slug into words and map Lower/Upper to Early/Late; `UNIT_NAME` raised to 24. Graduated rule: run a label check on generated names (no camelCase) whenever the chart pin changes.
- **The band showed the epoch, not the period.** Cause: `deep_band` picked the finest rank available. Fix: period, then era, then eon, as the directive says.
- **An emulator anchor tested a moment the face never draws** (23:39:30 on a minute face). Fix: the anchor is 23:40. Graduated rule: pin emulator times to minute boundaries unless the face is ticking seconds.
- **A contract test was missing** (Python vs C at 100 times). Fix: `tests/test_c_mapping.py`.
- **Infrastructure (log only):** in the 2026-10-01 full emulator run, the midnight scenario's `pebble install --logs` hit a `libpebble2` TimeoutError (the emulator stopped answering after 15 installs). It passed 2/2 after `pebble kill`. Also, piping `emulator_check.py` through `tail` hides its exit code, so read the PASS/FAIL lines rather than the exit status.

## 2026-10-01: store releases went live instead of drafts
- The owner asked for drafts. `pebble publish --non-interactive` without `--is-published` still made every release public, both new listings and updates. Cause: a project note (straight-ahead build_and_emulate.md step 3) said this flag controls drafts, and it doesn't. Graduated rule: `pebble publish` means public; stage drafts on the dashboard. Recorded in from-here/knowledge/procedural/emulator_and_release.md.
