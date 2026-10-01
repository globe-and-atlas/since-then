# Decisions

## Initial Decision

- Template profile: `workflow-python`
- Deploy target: `local-only`
- Runtime: `python`

## 2026-09-29 — Time-based lenses only; Deep Time first
- **Decision:** Epoch Watch maps time spans onto the 24-hour day. Narrative lenses (the Odyssey, the Hero's Journey, film arcs) are scrapped.
- **Decision:** Deep Time ships alone. Holocene, Common Era and Second Millennium follow only after a 7-day wrist gate.
- **Decision:** No phone JS in v1. Data is compiled into the watch as a resource.
- **Alternatives:** 6-lens selector at launch (rejected: two ideas in one face, hard to explain in a sentence); log time scale (rejected: loses the "humans in the last 6 seconds" payoff).
- **Reason:** From Here's reception came from one glanceable idea; the offline design avoids the AppMessage failure class From Here hit on hardware.
- Directive: `directives/build_epoch_watch.md`.

## 2026-09-29 — 00:00 is Earth's formation
- **Decision:** Deep Time's 00:00 = 4,540 Ma (Earth), not 4,567.3 Ma (Solar System, ICS Hadean base). Owner's call. The Hadean is clipped to start at 00:00.

## 2026-09-29 — Name: Since Then
- **Decision:** Store name **Since Then**, tagline "All in a day". The repo stays `epoch-watch`.
- **Alternatives:** Deep Time (free on Pebble, but crowded elsewhere: DeepTime for Geology, Deep Time Walk); All in a Day (clearest description; kept as the tagline); From Then, Long Story Short, All This Time (all free on the Pebble store).
- **Reason:** It pairs with From Here in the Globe & Atlas set, fits every lens (Earth, Holocene, Common Era, the year 1000), and no store title uses it. Put "deep time" in the description for search.

## 2026-09-30 — Historical lenses now, not after the gate
- **Decision:** Holocene, Common Era and Second Millennium are built alongside Deep Time. Owner's call, overriding the 7-day wrist gate.
- **Design:** one shared `history.csv` filtered by span; the watch maps years to clock time using the real date; gap rule ≤ 30 clock minutes per lens; regional balance (no region over 40%; every region represented).
