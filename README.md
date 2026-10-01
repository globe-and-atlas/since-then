# Since Then

*All in a day.* A Pebble Time 2 watchface by Globe & Atlas that squeezes a span of time into 24 hours. Midnight is the start of the span and the next midnight is now.

- **Deep Time** (default): Earth's 4,540 million years. Oxygen fills the air mid-morning, animals appear after 21:00, the dinosaurs die at 23:39, and humans arrive six seconds before midnight. The last minute ticks by the second.
- **Holocene**: since the end of the last ice age, 9700 BCE (about 8 years a minute).
- **Common Era**: since 1 CE (about 1.4 years a minute).
- **Second Millennium**: since 1001 CE (about 0.7 years a minute).

The face shows the moment's age or year, its geological period or century, and the latest event on the timeline. Every event is checked against a cited source (`knowledge/domain/*_sources.md`).

Sibling of [From Here](https://github.com/globe-and-atlas/from-here). Fully offline: no phone connection needed.

**Status:** builds and passes its emulator checks; not yet tested on a physical watch. See [`directives/build_epoch_watch.md`](directives/build_epoch_watch.md) and [`knowledge/procedural/build_and_check.md`](knowledge/procedural/build_and_check.md).

## Credits
- Geologic time: ICS International Chronostratigraphic Chart v2024-12 (Cohen, Harper, Gibbard & Car 2025, *Episodes* 48:105-115), CC BY 4.0.
- Events: the Wikipedia articles and papers cited in `data/*/events.csv`.

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
