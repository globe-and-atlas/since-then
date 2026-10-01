---
generated_by: "Claude Code CLI (claude-opus-5-5)"
timestamp: "2026-09-30T11:30:00-05:00"
---

# History sources: verification record

`python3 execution/verify_sources.py --data history` checks each row of `data/history/events.csv`: the cited page must state a year within ± max(uncertainty, 1). BC rows need "N BC" (including "N–M BC" ranges). The report goes to `.tmp/source_report_history.md`.

Result on 2026-09-30: 226 MATCH, 2 hand-checked.

| Year | Row | Verdict | Why |
|---|---|---|---|
| 340 ± 10 | Ezana makes Aksum Christian | OK | The page: ruler of Aksum "320s – c. 360 AD"; the conversion falls in his reign. |
| 1312 ± 8 | Mansa Musa becomes ruler | OK (approximate) | The page: "ascended to power in the early 1300s under unclear circumstances"; 1312 is the usual date. Shown as "c. 1312". |

## Fixed on 2026-09-30
- 'Ain Ghazal statues: the page title is "Ayn Ghazal statues".
- Great Pyramid: the page says "built c. 2600 BC", so the row is now −2600, "is built", not "−2560, finished".
- Mansa Musa: the uncertainty went from 0 to 8.
- Checker bugs: two-digit BC years ("44 BC") were missed, and years followed by a comma ("in 1652,") were rejected.

## Sources
- Prehistory leans on Wikipedia's "Nth millennium BC" pages, which list dated events.
- Historical rows cite the event's own article.
