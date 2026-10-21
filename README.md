# P30 — EIA data consistency audit

**Field:** Energy / data verification  
**Size:** Medium (one project season)  
**Time:** 2 months

## Question
How often do EIA-860, EIA-923 and state records disagree on the same plant's capacity, dates and location, and does it change any published total?

## Why it matters
Verification of data, not just code, is in Examen Silentii's scope, and PUDL users would care.

## Builds on
PUDL familiarity

## Method
1. Match plants across sources (PUDL helps)
2. Classify disagreements; check a sample by hand against permits/news
3. Recompute a state capacity total under each source

## Deliverable
Report; corrections sent to EIA/PUDL.

## Risks
Entity matching errors masquerade as data errors.

## Before you start: novelty check
Search Google Scholar / arXiv / GitHub for: _EIA-860 data quality inconsistencies_. If the question is already answered, narrow it or pick another project.

## Possible outlet
Scientific Data (data descriptor); PUDL blog

## Log
_(dates, decisions, results)_
- 2026-10-21: Narrowed to wind: the US Wind Turbine Database (USWTDB v9.1, 28 Sep 2026; built by USGS and Berkeley Lab, Rand et al. 2020) against EIA-860 2025, matched on EIA plant code (p30_wind_check.py; p30_findings.txt, p30_plants.csv). Onshore projects completed by 2025: EIA has 1,368 wind plants, 159,560 MW.
  - Inside USWTDB: 3,398 turbines in 423 projects carry no EIA plant code; 3,480 have no turbine capacity; 316 of 1,859 projects list fewer or more turbines than their own stated count; 97 have a stated capacity that differs from the sum of their turbines.
  - Coverage: 95 EIA wind plants (2,728 MW) have no turbines in USWTDB under their code; 72 USWTDB codes (3,159 MW) have no operable EIA wind.
  - Capacity: 79 matched plants differ by more than 10% and 5 MW. Grouping codes within 10 km (to absorb code splits) leaves 54 groups of 805 that genuinely disagree.
  - Examples checked by hand: NedPower Mount Storm (WV, 2008) lists 3 of its 132 turbines; Ekola Flats (WY) 51 of 63; Traverse (OK) 299 of 356. Headwaters II (IN) carries Headwaters I's EIA code (58416) although EIA lists it as 62592. Cedro Hill (TX) is reported to EIA as two 150 MW generators (300 MW), but the farm is 100 turbines repowered from 150 to 160 MW in 2024-25 (Clearway; North American Windpower), so EIA appears to double-count about 140 MW. Foote Creek Rim (WY): EIA 134.8 MW, USWTDB 11 turbines (46.2 MW); not yet resolved.
- Next: classify all 54 disagreeing groups (construction lag, missing turbines, code errors, EIA double counts), hand-check a sample, then report USWTDB items to Joe Rand and EIA items to EIA.
