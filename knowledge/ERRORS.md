# Errors

Record deterministic errors, root causes, and fixes here.

## 2026-09-30: event sources written from memory
- **A wrong DOI and a non-existent page** in `events.csv` (1630 Ma and 385 Ma), plus two pages that didn't support their dates. Cause: sources were attached from memory, not looked up. Fix: `execution/verify_sources.py` fetches every source and checks the stated ages. Hand-checked rows are recorded in `domain/deep_time_sources.md`. Graduated rule: run the verifier before committing any `events.csv` change.
- **Wikipedia API rate limit (HTTP 429)** at about one request per 0.3 s. The script now waits 1.5 s and honours Retry-After.
