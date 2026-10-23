# P30: findings checked against outside sources (22 October 2026)

Sources compared: US Wind Turbine Database v9.1 (28 Sep 2026) and EIA-860 2025 (operable onshore wind). Each item below was checked by hand against a source independent of both, or against the database's own fields.

## Items for EIA (EIA-860 appears wrong)

| Plant (EIA code) | EIA-860 2025 | Independent source | Difference |
|---|---|---|---|
| Cedro Hill, TX (57260) | Two generators of 150 MW each: 300 MW | 100 turbines, repowered from 150 to 160 MW in 2024-25 (Clearway; North American Windpower; Orrick). USWTDB: 100 turbines, 159.7 MW | About 140 MW counted twice; the repowering appears to have been added as a second generator without the first being retired |
| Hawkeye Power Partners, IA (55816) | 42 MW, 1999, operable | Global Energy Monitor lists the original 41 MW Cerro Gordo phase (1999, alias Hawkeye Power) as retired in 2020, replaced the same year by Cerro Gordo repower, which EIA also lists (63287, 42 MW, 2020). USWTDB has only the 16 repowered turbines | Likely 42 MW counted twice |
| Bearkat II, TX (59972, generator BRKA2) | Listed as cancelled (103.4 MW); no operating Bearkat II | Developers announced commercial operation of the 162 MW second phase (North American Windpower; Tri Global Energy and CIP). USWTDB: 47 Vestas V126-3.45 turbines, 162.2 MW, under code 63342 | About 162 MW operating but missing from EIA's operable list |
| Palo Duro Wind, TX (59475) | 282.3 MW | 147 GE 1.7-100 turbines, 249.9 MW (USWTDB; The Wind Power) | About 32 MW higher in EIA |
| Lost Creek Wind, MO (57189) | 168 MW | 100 GE 1.5 MW turbines, 150 MW (GE announcement; USWTDB) | 18 MW higher in EIA; possibly an uprate, to be asked rather than asserted |

## Items for the USWTDB team (the database appears wrong or incomplete)

1. **Turbines missing from 13 projects whose own project fields are complete.** The project's stated turbine count and capacity agree with EIA, but fewer turbines are listed. Largest: NedPower Mount Storm, WV (3 of 132 listed), Traverse, OK (299 of 356), Brazos, TX, Forest Creek, TX, Sundance, OK, Ekola Flats, WY (51 of 63). In all, about 1,100 MW of listed capacity is missing.
2. **Foote Creek I repowering, WY.** 13 turbines 1.2 km from Foote Creek Rim are listed as "unknown Carbon County" (2020) with no EIA code, model or capacity. These match PacifiCorp's 2020 repowering of Foote Creek I with 13 Vestas turbines (KSL, August 2019).
3. **Plant codes.**
   - Headwaters II, IN (44 turbines, 2021) carries Headwaters I's code 58416; EIA lists it as 62592.
   - Western Spirit, NM: all 377 turbines carry Red Cloud's code 63981; EIA splits the project into Red Cloud (63981), Clines Corners (64054), Tecolote (64066) and Duran Mesa (64065). The totals agree (1,056 and 1,052 MW).
   - Great Prairie Wind, TX: the database uses codes 64665, 64666, 64667 and 65704 for four phases; EIA has one plant (64665, 1,027 MW). The totals agree (1,029 MW).
4. **Vienna I and II repowering, IA (57874).** Turbine capacity is given as 3,100 kW for 60 turbines (186 MW), but the turbines are downrated and the plant is about 152 MW (The Wind Power; EIA 150.2 MW).
5. **Turbines still listed at seven plant codes that EIA records as retired or cancelled**, including Medicine Bow, WY (692). These may be turbines since removed; worth a check against recent imagery.

## Timing differences, not errors

Badger Wind, ND (250 MW) and Big Sampson Wind, TX (265 MW) are in the database as built in 2025 but in EIA-860 2025 as proposed, under construction or testing. The database records turbines once they are visible; EIA records commercial operation.
