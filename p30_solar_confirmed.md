# P30 solar: EIA-860 plant locations checked against imagery (23 October 2026)

Sources compared: US Large-Scale Solar Photovoltaic Database (USPVDB) v4.0 (14 April 2026) and EIA-860 2025 (plant locations, sheet 2___Plant). USPVDB takes capacity, year and name from EIA-860, so only its independently digitised locations and array areas are compared (`p30_solar_check.py`).

Method: the six largest plants whose EIA-860 location is more than 25 km from the USPVDB array were checked by hand in Google Maps satellite view, at both points. Imagery dates were not recorded.

| Plant (EIA code) | MWac | Distance | USPVDB point | EIA-860 point | Result |
|---|---|---|---|---|---|
| Dodge Flat, NV (63913) | 200 | 118 km | 39.6561, -119.3459: three blocks of panels | 40.7130, -119.4672: no panels; open ground beside County Road 447 | EIA location wrong |
| Buckthorn Westex, TX (60044) | 154 | 63 km | 31.0808, -102.8393: panels | 30.5755, -102.5513: no panels | EIA location wrong |
| Mockingbird Solar Center, TX (64347) | 471 | 39 km | 33.6490, -95.7157: panels | 33.3917, -95.4252: no panels | EIA location wrong |
| Cutlass Solar II, TX (66262) | 203 | 38 km | 29.2408, -95.4217: panels | 29.3900, -95.7800: no panels | EIA location wrong |
| CA Flats Solar 150, CA (60034) | 150 | 26 km | 35.8350, -120.2973: panels | 35.6156, -120.4044: south-west of the arrays, no panels | EIA location wrong |
| CA Flats Solar 130, CA (60033) | 130 | 29 km | 35.8719, -120.3316: panels | 35.6156, -120.4044 (same point as CA Flats 150) | EIA location wrong |

All six confirmed: in each case the USPVDB array is where the panels are, and the EIA-860 point has none. Together they are 1,308 MWac placed 26 to 118 km from where they are.

Not an explanation: coarse coordinates. Only 12 of the 111 plants more than 10 km out have EIA coordinates with two decimal places or fewer (Cutlass Solar II is one), against 2.9% of all plants. The others carry five or six decimal places, so the errors are not rounding. Separately, 98 EIA-860 points are shared by more than one plant, as CA Flats 130 and 150 are.

## Still to check

- The other 105 plants more than 10 km from their arrays (`p30_solar_findings.txt`, section 1), 3,607 MWac.
- The capacity-density outliers (section 2) and the EIA plants missing from USPVDB (section 3).

## Why it matters

Grid models and maps that place generators by their EIA-860 coordinates inherit these errors: a plant 118 km from its true location can be attached to the wrong part of the network. Whether GridSFM (P31) uses these coordinates has not been checked.
