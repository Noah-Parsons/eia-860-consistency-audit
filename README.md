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
- 2026-10-22: Classified the 54 disagreeing groups (p30_classify.py; p30_groups.csv): turbines missing from USWTDB though its project fields agree with EIA, 13 groups (net -1,116 MW); capacity differs with every turbine listed, 15 (includes Cedro Hill); plant-code mix-ups, 4 (Headwaters I/II, Sherbino, Great Prairie); in USWTDB but without a plant code, 4 (Lundgren, Hart, Duran Mesa, Dinosaur Point); USWTDB lists turbines at codes EIA records as retired or cancelled, 7 (incl. Medicine Bow, WY), or as proposed, 2 (Badger Wind ND, Big Sampson TX); recent build, 1 (Wagon Wheel); unexplained, 8 (Buffalo Gap complex, Baron Winds, small Texas sites, the NREL test site, two in Puerto Rico).
- 2026-10-22: Hand-checked against outside sources (p30_confirmed.md). EIA items: Cedro Hill double count (~140 MW); Hawkeye Power Partners still operable after its 2020 replacement by Cerro Gordo repower (~42 MW twice); Bearkat II (162 MW, operating per developers) listed as cancelled; Palo Duro 282.3 vs 249.9 MW; Lost Creek 168 vs 150 MW (ask, may be an uprate). USWTDB items: turbines missing from 13 complete projects (NedPower Mount Storm 3 of 132); Foote Creek I repower's 13 turbines listed as "unknown Carbon County" without code, model or capacity; plant-code splits and mix-ups (Headwaters II, Western Spirit, Great Prairie); Vienna repower turbine capacity overstated (186 vs ~152 MW); turbines at 7 codes EIA lists as retired. Badger Wind and Big Sampson are timing differences, not errors.
- Next: draft the email to Joe Rand (USWTDB items, plus the updated queue paper) and the report to EIA.
