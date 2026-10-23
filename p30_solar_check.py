"""P30, solar: the US Large-Scale Solar Photovoltaic Database (USPVDB) against EIA-860.

Usage (from the P30 folder):
    py p30_solar_check.py
Inputs: uspvdb_*.csv in this folder; EIA-860 2025 from ../WY-Grid-Map/eia8602025.zip.

USPVDB takes its capacity, year and name from EIA-860, so comparing capacities would be
circular. What USPVDB adds independently is where the panels are and how much ground they
cover, both drawn from aerial imagery. Three checks use only that:

  1. Location: EIA-860's plant coordinates against the mapped arrays.
  2. Capacity density: DC capacity per km2 of mapped array. Modules convert at most about
     23% of 1000 W/m2, so even panels laid edge to edge with no gaps hold about 230 MWdc per
     km2. A higher figure means the capacity is overstated or the arrays are not all mapped.
     Facilities whose imagery predates their first full year are left out (construction).
  3. Coverage: EIA plants of 1 MW or more, every unit in service by the end of 2022, that
     USPVDB does not list.

Writes p30_solar_findings.txt and p30_solar_plants.csv.
"""
import glob
import io
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
MAX_DENSITY = 230.0  # MWdc per km2: 23% efficient modules covering the whole area
FAR_KM = 10.0

out = io.StringIO()


def say(*a):
    print(*a)
    print(*a, file=out)


def km(lat1, lon1, lat2, lon2):
    p1, p2 = np.radians(lat1), np.radians(lat2)
    a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(np.radians(lon2 - lon1) / 2) ** 2
    return 6371.0 * 2 * np.arcsin(np.sqrt(a))


src = sorted(HERE.glob("uspvdb_*.csv"))[-1]
u = pd.read_csv(src)
u["density"] = u.p_cap_dc / (u.p_area / 1e6)
u["img_year"] = u.p_img_date // 10000

z = glob.glob(str(HERE.parent / "WY-Grid-Map" / "eia860*.zip"))[0]
with zipfile.ZipFile(z) as zf:
    def sheet(prefix, name):
        return pd.read_excel(io.BytesIO(zf.read(next(n for n in zf.namelist() if n.startswith(prefix)))), name, header=1)
    gen = sheet("3_1_Generator", "Operable")
    plant = sheet("2___Plant", 0)
for t in (gen, plant):
    t["Plant Code"] = pd.to_numeric(t["Plant Code"], errors="coerce")
pv = gen[gen.Technology.str.contains("Photovoltaic", na=False)]
eia = (pv.groupby("Plant Code")
       .agg(eia_mw_ac=("Nameplate Capacity (MW)", "sum"), eia_first=("Operating Year", "min"),
            eia_last=("Operating Year", "max"))
       .join(plant.set_index("Plant Code")[["Plant Name", "State", "Latitude", "Longitude"]]))
for c in ("Latitude", "Longitude"):
    eia[c] = pd.to_numeric(eia[c], errors="coerce")

say(f"USPVDB {src.name}: {len(u):,} facilities, {u.p_cap_ac.sum():,.0f} MWac")
say(f"EIA-860 2025: {len(eia):,} plants with operable PV, {eia.eia_mw_ac.sum():,.0f} MWac")

m = u.merge(eia, left_on="eia_id", right_index=True, how="left")
m["dist_km"] = km(m.ylat, m.xlong, m.Latitude, m.Longitude)

say("\n1. Location: EIA-860 plant coordinates against the mapped arrays")
for k in (10, 25, 50, 100):
    sub = m[m.dist_km > k]
    say(f"  more than {k:>3} km apart: {len(sub):>4} plants, {sub.p_cap_ac.sum():,.0f} MWac")
say("  largest plants more than 10 km apart:")
cols = ["eia_id", "p_name", "p_state", "p_cap_ac", "dist_km", "ylat", "xlong", "Latitude", "Longitude", "p_dig_conf"]
say(m[m.dist_km > FAR_KM].sort_values("p_cap_ac", ascending=False)[cols].head(15).round(4).to_string(index=False))

say(f"\n2. Capacity density above {MAX_DENSITY:.0f} MWdc/km2 (imagery after the first year)")
dense = m[(m.density > MAX_DENSITY) & (m.img_year > m.p_year)]
say(f"  {len(dense)} facilities, {dense.p_cap_ac.sum():,.0f} MWac")
cols = ["eia_id", "p_name", "p_state", "p_year", "img_year", "multi_poly", "p_cap_ac", "eia_mw_ac", "p_cap_dc", "p_area", "density"]
say(dense.sort_values("p_cap_ac", ascending=False)[cols].head(15).round(1).to_string(index=False))

say("\n3. EIA plants of 1 MW or more, in service by 2022, not in USPVDB")
miss = eia[(eia.eia_mw_ac >= 1) & (eia.eia_last <= 2022) & ~eia.index.isin(u.eia_id)]
say(f"  {len(miss)} plants, {miss.eia_mw_ac.sum():,.0f} MWac")
say(miss.sort_values("eia_mw_ac", ascending=False)[["Plant Name", "State", "eia_mw_ac", "eia_first", "eia_last"]].head(15).to_string())

m["issues"] = ""
m.loc[m.dist_km > FAR_KM, "issues"] += f"over {FAR_KM:.0f} km apart;"
m.loc[dense.index, "issues"] += "density above physical limit;"
m.sort_values("p_cap_ac", ascending=False).to_csv(HERE / "p30_solar_plants.csv", index=False)
(HERE / "p30_solar_findings.txt").write_text(out.getvalue(), encoding="utf-8")
print("\nSaved p30_solar_findings.txt and p30_solar_plants.csv")
