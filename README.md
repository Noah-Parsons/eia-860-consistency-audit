# EIA-860 Data Consistency Audit

A plant-by-plant check of the US Energy Information Administration's generator inventory (Form EIA-860) against independent national databases built from aerial imagery and other sources. The question is how often the two disagree, which one is wrong when they do, and whether the errors change any published total.

| | |
|---|---|
| **Field** | Energy data; verification of public datasets |
| **Status** | Active. Wind and solar checks complete. Confirmed EIA-860 items reported to EIA (22 and 23 October 2026); wind database items reported to the US Wind Turbine Database team at Lawrence Berkeley National Laboratory (22 October 2026) |
| **Started** | 21 October 2026 |
| **Builds on** | PUDL familiarity |
| **Possible outlets** | Scientific Data (data descriptor); PUDL blog |

## Question

How often do EIA-860 and independent records disagree on the same plant's capacity, status and location, and do the disagreements change any published total?

## Sources

| Dataset | Version | What in it is independent of EIA-860 |
|---|---|---|
| EIA-860, 2025 (generator, wind and plant files) | Released September 2026 | (the inventory under test) |
| US Wind Turbine Database (USWTDB), USGS and Lawrence Berkeley National Laboratory | v9.1, 28 September 2026 | Turbine locations, counts, models and capacities, compiled from imagery, FAA records and manufacturers. It carries the EIA plant code as a link |
| US Large-Scale Solar Photovoltaic Database (USPVDB), USGS and Lawrence Berkeley National Laboratory | v4.0, April 2026 | Array locations and areas, digitised from imagery. Capacity, name and year are taken from EIA-860, so only location and area are independent |

## Method

1. **Match on EIA plant code**, then group neighbouring codes within 10 km, so that a plant one database splits into phases and the other does not is not counted as a disagreement.
2. **Classify each remaining disagreement** by kind: turbines missing, capacity different, code assignment, retired or proposed in EIA, timing.
3. **Check by hand** against a source independent of both databases: developers' announcements, trade press, Global Energy Monitor, satellite imagery.
4. **Say which source appears wrong**, and raise as a question rather than an error anything an uprate or a reporting date could explain.

## Results

### 1. Wind (`p30_wind_check.py`, `p30_classify.py`)

EIA-860 2025 has 1,368 plants with operable onshore wind, 159,560 MW; USWTDB has 76,165 onshore turbines in projects completed by 2025.

- **Inside USWTDB:** 3,398 turbines in 423 projects carry no EIA plant code; 3,480 have no turbine capacity; 316 of 1,859 projects list a different number of turbines from their own stated count.
- **Coverage:** 95 EIA wind plants (2,728 MW) have no turbines in USWTDB under their code; 72 USWTDB codes (3,159 MW) have no operable EIA wind.
- **Capacity:** of 1,273 matched plants, 79 differ by more than 10% and 5 MW. After grouping neighbouring codes, 54 of 809 groups still disagree:

| Kind | Groups | Net difference (USWTDB minus EIA) |
|---|---|---|
| Turbines missing from USWTDB, its project fields complete | 13 | −1,116 MW |
| Capacity differs with every turbine listed | 15 | −348 MW |
| Plant-code assignment | 4 | +430 MW |
| In USWTDB without a plant code | 4 | −560 MW |
| Retired or cancelled in EIA | 7 | +86 MW |
| Proposed in EIA, built in USWTDB (timing) | 2 | +528 MW |
| Recent build | 1 | −595 MW |
| Unexplained | 8 | +21 MW |

### 2. Solar locations (`p30_solar_check.py`)

111 plants with operable photovoltaic capacity in EIA-860 lie more than 10 km from the USPVDB arrays carrying their code. The six largest were checked on satellite imagery: in each, the panels are at the USPVDB location and there are none at the EIA-860 coordinates.

| Plant (EIA code), state | Capacity | Distance between EIA-860 point and arrays |
|---|---|---|
| Dodge Flat (63913), NV | 200 MW | 118 km |
| Buckthorn Westex (60044), TX | 154 MW | 63 km |
| Mockingbird Solar Center (64347), TX | 471 MW | 39 km |
| Cutlass Solar II (66262), TX | 203 MW | 38 km |
| CA Flats Solar 150 (60034), CA | 150 MW | 26 km |
| CA Flats Solar 130 (60033), CA | 130 MW | 29 km |

The two CA Flats plants share one EIA-860 coordinate. Only 12 of the 111 have coarsely rounded coordinates, so rounding cannot explain most of the offsets. The remaining 105 have not been checked by hand.

### 3. Repowering double counts, national search (`p30_repower_check.py`)

Cedro Hill and Hawkeye, found by hand, are repowerings counted twice: the new turbines were added to EIA-860 as a second generator or a second plant while the old capacity stayed operable. The search looked for the same two patterns in all 1,368 operable wind plants.

- **No further double counts.** Cedro Hill is the only plant with a repeated generator that USWTDB shows once; Hawkeye is the only old plant left operable beside its replacement. Two other matches were checked and ruled out: Beaver Creek, IA, is a USWTDB code split, and Crescent Ridge, IL, was repowered in place in January 2022 and EIA's 28 turbines are correct.
- **Smaller EIA-860 items found on the way:** Caprock, NM (turbine model updated after its February 2025 repowering, but the turbine count of 80 and capacity of 100 MW were not; the repowering is 20 turbines of 4.5 MW); Lake Benton II, MN, and GSG, IL (turbine counts predate repowering); Highland and Adams, IA (each plant's turbine total entered on one small generator). Details in `p30_confirmed.md`.

## Findings

### EIA-860 items

| Plant (EIA code), state | EIA-860 2025 | Independent evidence | Status |
|---|---|---|---|
| Cedro Hill (57260), TX | Two 150 MW generators, 300 MW | 100 turbines, repowered to about 160 MW in 2024–25 | Reported 22 Oct |
| Hawkeye Power Partners (55816), IA | 42 MW, operable | Replaced in 2020 by Cerro Gordo repower (63287), also listed | Reported 22 Oct |
| Bearkat II (59972, BRKA2), TX | Cancelled | 162 MW in commercial operation; 47 turbines in USWTDB | Reported 22 Oct |
| Palo Duro (59475), TX | 282.3 MW | 147 GE 1.7-100 turbines, 249.9 MW | Reported 22 Oct |
| Lost Creek (57189), MO | 168 MW | 100 turbines of 1.5 MW; may be an uprate | Reported 22 Oct, as a question |
| Six solar plants (table above) | Coordinates 26–118 km from the arrays | Satellite imagery | Reported 23 Oct |
| Caprock (56293), NM | 100 MW, 80 turbines | 20 turbines of 4.5 MW since February 2025 | Not yet reported |
| Lake Benton II (55265), GSG (56450), Highland (58883), Adams (59637) | Turbine counts | USWTDB | Not yet reported |

### USWTDB items (reported to LBNL, 22 October)

1. Turbines missing from 13 projects whose own fields are complete, about 1,100 MW in all (largest: NedPower Mount Storm, WV, 3 of 132 listed).
2. Foote Creek I repowering, WY: 13 turbines listed as "unknown Carbon County" without code, model or capacity.
3. Plant codes: Headwaters II carries Headwaters I's code; Western Spirit and Great Prairie are split differently from EIA (totals agree).
4. Vienna I and II repowering, IA: turbine capacity overstated (186 MW against about 152 MW).
5. Turbines at seven codes EIA records as retired or cancelled.
6. Not yet reported: Crescent Ridge, IL, 22 of its 28 repowered turbines listed as "unknown Bureau County", without attributes.

### Not errors

Badger Wind (ND) and Big Sampson (TX) are built in USWTDB but proposed in EIA-860 2025: the databases record different events (turbines visible, commercial operation). Beaver Creek (IA), Western Spirit (NM) and Great Prairie (TX) are code splits whose totals agree.

## Effect on totals

On the confirmed EIA-860 wind items, the overstatements (Cedro Hill about 140 MW, Hawkeye 42 MW, Palo Duro about 32 MW) and the omission (Bearkat II, 162 MW) nearly cancel: about +52 MW net nationally, or +70 MW if Lost Creek is an error, against 159,560 MW (0.03–0.04%). In Texas the three items net to about +10 MW. The errors matter for individual plants and for anyone using plant-level data, but not for national or state totals. The solar errors are of location, not capacity.

## Reproducing

```
py p30_wind_check.py        # writes p30_findings.txt and p30_plants.csv
py p30_classify.py          # writes p30_groups.csv
py p30_solar_check.py       # writes p30_solar_findings.txt and p30_solar_plants.csv
py p30_repower_check.py     # writes p30_repower_findings.txt
```

Inputs: the USWTDB CSV (`uswtdb_V9_1_*.csv`, https://eerscmap.usgs.gov/uswtdb/) and USPVDB CSV (`uspvdb_v4_0_*.csv`, https://eerscmap.usgs.gov/uspvdb/) in this folder, and the EIA-860 2025 zip in `../WY-Grid-Map/`. The database files are not committed because of their size.

## Files

| File | Contents |
|---|---|
| `p30_wind_check.py`, `p30_findings.txt`, `p30_plants.csv` | Wind comparison and its results, one row per plant code |
| `p30_classify.py`, `p30_groups.csv` | Grouping of neighbouring codes and classification of disagreements |
| `p30_confirmed.md` | Wind items checked by hand against outside sources, and the repowering search |
| `p30_solar_check.py`, `p30_solar_findings.txt`, `p30_solar_plants.csv` | Solar location comparison and its results |
| `p30_solar_confirmed.md` | Solar items checked on imagery |
| `p30_repower_check.py`, `p30_repower_findings.txt` | National search for repowerings counted twice |
| `CHANGELOG.txt` | USWTDB change log, kept for reference |

## Planned

1. Report the remaining EIA-860 items (Caprock and the turbine counts) and the Crescent Ridge USWTDB item.
2. Check the remaining 105 solar location offsets, at least those above 100 MW.
3. Novelty check against existing audits of EIA-860.
4. Compare against EIA-923 generation, to test capacities against output.

## Log

- **21 October 2026.** Narrowed to wind: USWTDB v9.1 against EIA-860 2025, matched on EIA plant code.
- **22 October 2026.** Classified the 54 disagreeing groups; hand-checked the largest against outside sources. Reported five EIA-860 items to EIA and the USWTDB items to LBNL.
- **23 October 2026.** Solar location check against USPVDB v4.0; six offsets confirmed on imagery and reported to EIA. National repowering search: no further double counts; smaller turbine-count items found.
- **25 October 2026.** README rewritten.
