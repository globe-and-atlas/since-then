---
generated_by: "Claude Code CLI (claude-opus-5-5)"
timestamp: "2026-09-30T23:00:00-05:00"
---

# Build and check Since Then

```bash
.venv/bin/python3 execution/fetch_ics_units.py            # ICS units (pinned commit); rarely needed
.venv/bin/python3 execution/build_deep_time.py            # validate + write watchface/src/c/deep_time_data.h
.venv/bin/python3 execution/build_history.py              # validate + write watchface/src/c/history_data.h
.venv/bin/python3 execution/verify_sources.py             # Deep Time sources -> .tmp/source_report.md
.venv/bin/python3 execution/verify_sources.py --data history
.venv/bin/python3 -m pytest tests -q
.venv/bin/python3 execution/emulator_check.py             # 17 checks, about 10 minutes; screenshots in .tmp/emulator/
.venv/bin/python3 execution/cloudpebble.py watchface .tmp/cloudpebble_sim   # must report "dropped: none"
(cd watchface && pebble build)                            # clean distributable build
```

- **Run the checks in this order.** After any `events.csv` edit, run the build (gaps, labels, balance), then the source check, then the tests. The tests fail if the generated header is stale.
- **Source check:** it is cached in `.tmp/sources/`, so reruns are offline. Wikipedia rate-limits at about 3 requests a second; the script waits 1.5 s and honours Retry-After.
- **Emulator test builds:**
  - `ST_TEST_SECONDS` and `ST_TEST_LENS` pin the clock and lens.
  - `ST_TEST_START_MINUTE` gives a running clock.
  - `emulator_check.py` always ends with a clean build.
- **Sideload:** `cd watchface && pebble install --cloudpebble build/watchface.pbw --logs`
