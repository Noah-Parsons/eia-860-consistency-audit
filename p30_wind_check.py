"""P30: the US Wind Turbine Database (USWTDB) against EIA-860, plant by plant.

Usage (from the P30 folder):
    py p30_wind_check.py
Inputs: uswtdb_V9_1_*.csv in this folder; EIA-860 2025 from ../WY-Grid-Map/eia8602025.zip.
Compares wind projects completed by the end of 2025 (USWTDB p_year <= 2025) with
EIA-860's operable wind generators at the end of 2025, matched on EIA plant code.

Writes p30_findings.txt and p30_plants.csv (one row per EIA plant code in either source).
"""
import glob
import io
import math
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
YEAR = 2025
CAP_TOL, CAP_MIN_MW, FAR_KM = 0.10, 5.0, 25.0

out = io.StringIO()


def say(*a):
    print(*a)
    print(*a, file=out)


def km(lat1, lon1, lat2, lon2):
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dp, dl = p2 - p1, np.radians(lon2 - lon1)
    a = np.sin(dp / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 6371.0 * 2 * np.arcsin(np.sqrt(a))


# ---------------------------------------------------------------- sources
u_all = pd.read_csv(sorted(HERE.glob("uswtdb_*.csv"))[-1], dtype={"eia_id": str})
u = u_all[(u_all.p_year <= YEAR) & (u_all.t_offshore == 0)].copy()
u["eia_id"] = pd.to_numeric(u.eia_id, errors="coerce")

z = glob.glob(str(HERE.parent / "WY-Grid-Map" / "eia860*.zip"))[0]
with zipfile.ZipFile(z) as zf:
    def sheet(prefix, name):
        data = zf.read(next(n for n in zf.namelist() if n.startswith(prefix)))
        return pd.read_excel(io.BytesIO(data), name, header=1)
    gen = sheet("3_1_Generator", "Operable")
    plant = sheet("2___Plant", 0)
CAP = "Nameplate Capacity (MW)"
gen["Plant Code"] = pd.to_numeric(gen["Plant Code"], errors="coerce")
plant["Plant Code"] = pd.to_numeric(plant["Plant Code"], errors="coerce")
wind = gen[gen.Technology.str.contains("Onshore Wind", na=False)]
eia = (wind.groupby("Plant Code")
       .agg(eia_name=("Plant Name", "first"), eia_state=("State", "first"),
            eia_mw=(CAP, "sum"), eia_units=(CAP, "size"),
            eia_first_year=("Operating Year", "min"))
       .join(plant.set_index("Plant Code")[["Latitude", "Longitude"]]))
any_eia = set(gen["Plant Code"].dropna().astype(int))

say(f"USWTDB {sorted(HERE.glob('uswtdb_*.csv'))[-1].name}: {len(u_all):,} turbines; "
    f"{len(u):,} onshore turbines in projects completed by {YEAR}")
say(f"EIA-860 {YEAR}: {len(eia):,} plants with operable onshore wind, {eia.eia_mw.sum():,.0f} MW")

# ---------------------------------------------------------------- USWTDB internal consistency
say("\n1. Inside USWTDB")
no_id = u[u.eia_id.isna()]
say(f"  turbines with no EIA plant code: {len(no_id):,} in {no_id.p_name.nunique()} projects "
    f"({no_id.t_cap.sum() / 1000:,.0f} MW where turbine capacity is given)")
say(f"  turbines with no turbine capacity: {u.t_cap.isna().sum():,}")
proj = u.groupby(["p_name", "p_year"]).agg(n=("case_id", "size"), p_tnum=("p_tnum", "first"),
                                           p_cap=("p_cap", "first"), t_sum=("t_cap", "sum"),
                                           t_missing=("t_cap", lambda s: s.isna().sum()))
bad_n = proj[proj.n != proj.p_tnum]
say(f"  projects whose stated turbine count (p_tnum) differs from the turbines listed: "
    f"{len(bad_n)} of {len(proj)}")
full = proj[(proj.t_missing == 0) & proj.p_cap.notna()]
bad_cap = full[(full.t_sum / 1000 - full.p_cap).abs() > np.maximum(CAP_MIN_MW, CAP_TOL * full.p_cap)]
say(f"  projects whose stated capacity (p_cap) differs from the sum of their turbines by more than "
    f"{CAP_TOL:.0%} and {CAP_MIN_MW:.0f} MW: {len(bad_cap)} of {len(full)}")

# ---------------------------------------------------------------- matched comparison
by_id = (u.dropna(subset=["eia_id"]).groupby("eia_id")
         .agg(usw_turbines=("case_id", "size"), usw_mw=("t_cap", lambda s: s.sum() / 1000),
              usw_cap_missing=("t_cap", lambda s: s.isna().sum()),
              usw_lat=("ylat", "median"), usw_lon=("xlong", "median"),
              usw_state=("t_state", lambda s: ";".join(sorted(set(s)))),
              usw_names=("p_name", lambda s: "; ".join(sorted(set(s))))))
by_id.index = by_id.index.astype(int)
both = eia.join(by_id, how="outer")
both.index.name = "eia_plant_code"

say("\n2. Coverage")
only_eia = both[both.usw_turbines.isna()]
say(f"  EIA wind plants with no turbines in USWTDB: {len(only_eia)} ({only_eia.eia_mw.sum():,.0f} MW)")
only_usw = both[both.eia_mw.isna()]
not_in_eia = only_usw[~only_usw.index.isin(any_eia)]
not_wind = only_usw[only_usw.index.isin(any_eia)]
say(f"  USWTDB plant codes with no operable EIA wind: {len(only_usw)} "
    f"({only_usw.usw_mw.sum():,.0f} MW): {len(not_wind)} are EIA plants without operable wind, "
    f"{len(not_in_eia)} are not operable EIA plants at all")

say("\n3. Capacity, where both sources have the plant")
m = both.dropna(subset=["eia_mw", "usw_turbines"]).copy()
m["diff_mw"] = m.usw_mw - m.eia_mw
comparable = m[m.usw_cap_missing == 0]
off = comparable[comparable.diff_mw.abs() > np.maximum(CAP_MIN_MW, CAP_TOL * comparable.eia_mw)]
say(f"  plants matched: {len(m)}; with every turbine's capacity given: {len(comparable)}")
say(f"  totals for those: EIA {comparable.eia_mw.sum():,.0f} MW, USWTDB {comparable.usw_mw.sum():,.0f} MW")
say(f"  disagree by more than {CAP_TOL:.0%} and {CAP_MIN_MW:.0f} MW: {len(off)} plants "
    f"(USWTDB higher: {(off.diff_mw > 0).sum()}, lower: {(off.diff_mw < 0).sum()})")

say("\n4. Location")
for c in ("Latitude", "Longitude"):
    m[c] = pd.to_numeric(m[c], errors="coerce")
m["dist_km"] = km(m.Latitude, m.Longitude, m.usw_lat, m.usw_lon)
far = m[m.dist_km > FAR_KM]
say(f"  EIA plant location more than {FAR_KM:.0f} km from the median of its turbines: {len(far)} plants")
st = m[m.apply(lambda r: r.eia_state not in str(r.usw_state).split(";"), axis=1)]
say(f"  EIA state not among the turbines' states: {len(st)} plants")

both["issues"] = ""
both.loc[only_eia.index, "issues"] += "no turbines in USWTDB;"
both.loc[only_usw.index, "issues"] += "no operable EIA wind;"
both.loc[off.index, "issues"] += "capacity differs;"
both.loc[far.index, "issues"] += f"over {FAR_KM:.0f} km apart;"
both.loc[st.index, "issues"] += "state differs;"
both = both.join(m[["diff_mw", "dist_km"]])
both.sort_values("eia_mw", ascending=False).to_csv(HERE / "p30_plants.csv")

say("\n5. Wyoming")
wy = both[(both.eia_state == "WY") | both.usw_state.fillna("").str.contains("WY")]
say(f"  plants: {len(wy)}; flagged: {(wy["issues"] != '').sum()}")
for code, r in wy[wy["issues"] != ""].iterrows():
    name = r.eia_name if isinstance(r.eia_name, str) else r.usw_names
    say(f"    {code} {name}: EIA {r.eia_mw if not pd.isna(r.eia_mw) else '-'} MW, "
        f"USWTDB {r.usw_mw if not pd.isna(r.usw_mw) else '-'} MW; {r.issues}")

(HERE / "p30_findings.txt").write_text(out.getvalue(), encoding="utf-8")
print("\nSaved p30_findings.txt and p30_plants.csv")
