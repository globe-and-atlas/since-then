---
generated_by: "Claude Code CLI (claude-opus-5-5)"
timestamp: "2026-09-30T09:30:00-05:00"
---

# Deep Time sources: verification record

`python3 execution/verify_sources.py` fetches every source in `data/deep_time/events.csv` (Wikipedia text; Crossref for DOIs) and writes `.tmp/source_report.md`. A row is MATCH when the source states an age within ± max(uncertainty, 5%). The rows below are CHECK, read by hand on 2026-09-30, and accepted for the stated reason. Re-read a row if its age, label or source changes.

| Age Ma | Row | Verdict | Why the script can't match it |
|---|---|---|---|
| 4150 | Moon closer, days short | OK (state) | Tidal acceleration has worked "for 4.5 billion years"; the Moon is retreating, so it was closer then. No single date exists. |
| 3770 | Nuvvuagittuq microfossils | OK | The abstract (Europe PMC) says "at least 3,770 million and possibly 4,280 million years". |
| 3700 | Isua stromatolites | OK | Title: "3,700-million-year-old microbial structures". |
| 3540 | Komatiite lavas | OK (state) | Komatiites are almost all Archean, 4.03–2.5 Ga. |
| 3400 | Strelley Pool cells | OK | Title: "3.4-billion-year-old rocks". |
| 3150 | Sun a fifth dimmer | OK (state) | The page gives 30% dimmer at 4.5 Ga; luminosity rises roughly linearly, giving ~21% dimmer at 3.15 Ga. |
| 3030 | Cyanobacteria may make oxygen | OK (state) | The page: evidence back to 2.7 Ga; "might have emerged 3.5 Ga". The label says "may". |
| 2960 | Pongola oxygen | OK | Title: "three billion years ago"; Pongola paleosols ~2.96 Ga. |
| 2650 | Methane haze | OK (state) | Title: "Neoarchaean" (2.8–2.5 Ga); no abstract was deposited. |
| 2600 | Stromatolite reefs | OK (state) | Stromatolites from 3.5 Ga, peaking at 1.25 Ga. |
| 2500 | McRae Shale whiff | OK | The abstract says "2501 ± 8 million years ago" (the script reads the ± 8 as the age). |
| 2100 | Francevillian biota | OK | "2.1-billion-year-old" (hyphenated). |
| 1630 | Multicellular eukaryotes | OK | Title: "1.63-billion-year-old multicellular eukaryotes" (Miao et al. 2024). |
| 1500 | Canfield ocean | OK (state) | Euxinic oceans across the Boring Billion, 1.8–0.8 Ga. |
| 1400 | 18.7-hour day | OK | Abstract: 1.4-billion-year-old rhythmites; day length 18.68 ± 0.25 h. |
| 1047 | Bangiomorpha | OK | Title: "Precise age of Bangiomorpha"; the paper gives 1047 +13/−17 Ma. No abstract in Crossref or Europe PMC. |
| 1000 | Rodinia assembled | OK | "assembled 1.26–0.90 billion years ago". |
| 950 | Ourasphaira | OK | Abstract: "approximately 1,010–890 million years ago". |
| 890 | Sponge fabric | OK | Abstract: "approximately 890-million-year-old reefs". |
| 558 | Dickinsonia | OK | Abstract: Ediacara biota 571–541 Ma; uncertainty widened to 15. |
| 385 | First forests, New York | OK | Abstract: mid Givetian; Mid Devonian 393–383 Ma; Cairo NY. |
| 225 | Mammaliaforms | OK | "radiated … during the Late Triassic" (237–201.4 Ma). |
| 1.0 | Wonderwerk fire | OK | "between 1.07 and 1.79 million years ago" (a range the script can't parse). |

## Fixed on 2026-09-30
- 1630 Ma: the DOI pointed to an unrelated Tibetan river paper. Replaced with 10.1126/sciadv.adk3208.
- 385 Ma: the Wikipedia page "Cairo fossil forest" does not exist. Replaced with Stein et al. 2020, Current Biology.
- 2750 Ma "huge lava floods" (Large igneous province page gave no date). Replaced with the Ventersdorp lavas at 2,715 Ma (Witwatersrand page).
- 2160 Ma red beds: the Red beds page has no dates. The source is now the Great Oxidation Event page.
- 2800 Ma cratons: now a state with ±300 (cratons formed across the Archean).
