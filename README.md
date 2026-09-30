# Since Then

*All in a day.* A Pebble Time 2 watchface by Globe & Atlas that stretches Earth's 4,540-million-year history over 24 hours. Midnight is Earth's formation and the next midnight is now. Oxygen fills the air mid-morning, animals appear after 21:00, the dinosaurs die at 23:39, and humans arrive six seconds before midnight.

Sibling of [From Here](https://github.com/globe-and-atlas/from-here). Fully offline: no phone connection needed.

**Status:** directive written, no code yet. See [`directives/build_epoch_watch.md`](directives/build_epoch_watch.md).

## Notes
- The face is always 24-hour: midnight to midnight is the span.
- On DST days a 23- or 25-hour day skips or repeats an hour of Earth history.

## Layout

```text
directives/     What to build, and the validation contract
execution/      Deterministic data build (CSV → watch resource)
data/           Curated, sourced units and events
watchface/      Pebble C app (Emery)
```

Scaffolded from `project-template` (`workflow-python` profile).
