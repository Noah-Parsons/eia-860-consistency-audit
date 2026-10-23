"""P30: national search of EIA-860 for wind repowerings counted twice.

Usage (from the P30 folder):
    py p30_repower_check.py
Inputs: uswtdb_V9_1_*.csv in this folder; EIA-860 2025 from ../WY-Grid-Map/eia8602025.zip.

A repowering replaces a wind farm's turbines. If EIA-860 records the new turbines as a new
generator or a new plant without retiring the old one, the farm's capacity is counted twice.
Cedro Hill (TX) and Hawkeye Power Partners (IA), found by hand, are the two known cases. This
script looks for the same pattern across every operable onshore wind plant, with two tests:

  A. Within a plant: two or more generators with the same turbine model and turbine count, where
     the US Wind Turbine Database (USWTDB) lists the plant's turbines only once and its own
     project count is complete, EIA's capacity is at least 1.3 times USWTDB's, and no other turbines of the same age stand within 10 km (which
     would mean USWTDB filed part of the plant under another code). (Cedro Hill: two 150 MW
     generators; 100 turbines on the ground.)
  B. Between plants: an operable EIA plant with no turbines under its code in USWTDB, no
     turbine within 5 km built before its operating year plus 2, and a newer EIA wind plant
     within 10 km. (Hawkeye: 1999 plant, no original turbines left, Cerro Gordo repower beside it.)

It also lists plants whose turbine model in EIA-860 was updated to a repowering's model while
the turbine count was not (test C), and generators whose turbine count implies less than
0.3 MW per turbine for a model rated above 2 MW (test D).

Writes p30_repower_findings.txt.
"""
import glob
import io
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
YEAR = 2025
CAP = "Nameplate Capacity (MW)"
out = io.StringIO()


def say(*a):
    print(*a)
    print(*a, file=out)


def km(lat1, lon1, lat2, lon2):
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dp, dl = p2 - p1, np.radians(np.asarray(lon2) - lon1)
    a = np.sin(dp / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 6371.0 * 2 * np.arcsin(np.sqrt(a))


# ---------------------------------------------------------------- sources
u_all = pd.read_csv(sorted(HERE.glob("uswtdb_*.csv"))[-1])
u = u_all[(u_all.p_year <= YEAR) & (u_all.t_offshore == 0)].copy()
u["code"] = pd.to_numeric(u.eia_id, errors="coerce")

z = glob.glob(str(HERE.parent / "WY-Grid-Map" / "eia860*.zip"))[0]
with zipfile.ZipFile(z) as zf:
    def sheet(prefix, name):
        data = zf.read(next(n for n in zf.namelist() if n.startswith(prefix)))
        return pd.read_excel(io.BytesIO(data), name, header=1)
    w = sheet("3_2_Wind", "Operable")
    plant = sheet("2___Plant", 0)
w = w[w.Technology.str.contains("Onshore Wind", na=False)].copy()
loc = plant.set_index("Plant Code")[["Latitude", "Longitude"]].apply(pd.to_numeric, errors="coerce")

eia = (w.groupby("Plant Code")
       .agg(name=("Plant Name", "first"), state=("State", "first"), gens=("Generator ID", "size"),
            mw=(CAP, "sum"), turbines=("Number of Turbines", "sum"),
            first_year=("Operating Year", "min"), last_year=("Operating Year", "max"))
       .join(loc))
usw = (u.dropna(subset=["code"]).groupby("code")
       .agg(u_turbines=("case_id", "size"), u_stated=("p_tnum", "max"), u_lat=("ylat", "median"), u_lon=("xlong", "median"),
            u_mw=("t_cap", lambda s: s.sum() / 1000), u_retrofit=("t_retrofit", "sum")))
m = eia.join(usw)

say(f"EIA-860 {YEAR}: {len(eia):,} plants with operable onshore wind, {eia.mw.sum():,.0f} MW, "
    f"{len(w):,} generators")
say(f"USWTDB {sorted(HERE.glob('uswtdb_*.csv'))[-1].name}: {len(u):,} onshore turbines built by {YEAR}")

# ---------------------------------------------------------------- A: duplicate generators
say("\nA. Generators repeated within a plant (same model and turbine count), where USWTDB lists the "
    "plant's turbines once and completely")
dup = (w.groupby(["Plant Code", "Number of Turbines", "Predominant Turbine Model Number"])
       .agg(k=("Generator ID", "size"), dup_mw=(CAP, "sum")).reset_index())
dup = dup[(dup.k >= 2) & (dup["Number of Turbines"] >= 10)].merge(m, left_on="Plant Code", right_index=True)


def same_age_nearby(r):
    """USWTDB turbines, under any code, within 10 km of the plant's turbines and built within a year of it."""
    near = u[(km(r.u_lat, r.u_lon, u.ylat.values, u.xlong.values) < 10)
             & u.p_year.between(r.first_year - 1, r.last_year + 1)]
    return len(near)


dup = dup.dropna(subset=["u_lat"])
dup["u_nearby"] = dup.apply(same_age_nearby, axis=1)
hit = dup[(dup.u_turbines == dup.u_stated) & (dup.turbines >= 1.5 * dup.u_turbines)
          & (dup.turbines >= 1.5 * dup.u_nearby) & (dup.mw >= 1.3 * dup.u_mw)]
split = dup[(dup.u_turbines == dup.u_stated) & (dup.turbines >= 1.5 * dup.u_turbines)
            & (dup.turbines < 1.5 * dup.u_nearby)]
say(f"  plants with a repeated generator of 10 or more turbines: {dup['Plant Code'].nunique()}; "
    f"where EIA exceeds USWTDB's complete count by half in turbines and 30% in capacity: "
    f"{hit['Plant Code'].nunique()}")
for _, r in hit.iterrows():
    say(f"    {int(r['Plant Code'])} {r['name']} ({r.state}): EIA {r.mw:.1f} MW, {r.turbines:.0f} turbines in "
        f"{r.gens} generators; USWTDB {r.u_turbines:.0f} turbines, {r.u_mw:.1f} MW "
        f"({r.u_retrofit:.0f} marked retrofit)")
for _, r in split.drop_duplicates("Plant Code").iterrows():
    say(f"    not counted: {int(r['Plant Code'])} {r['name']} ({r.state}), EIA {r.turbines:.0f} turbines; USWTDB "
        f"{r.u_turbines:.0f} under this code but {r.u_nearby} of the same age within 10 km")

# ---------------------------------------------------------------- B: old plant beside its repowering
say("\nB. Operable plants with no turbines in USWTDB, none of their age nearby, and a newer plant within 10 km")
mm = m.dropna(subset=["Latitude"])
rows = []
for code, r in mm[mm.u_turbines.isna()].iterrows():
    newer = mm[(km(r.Latitude, r.Longitude, mm.Latitude.values, mm.Longitude.values) < 10)
               & (mm.index != code) & (mm.first_year >= r.last_year + 3)]
    near_u = u[km(r.Latitude, r.Longitude, u.ylat.values, u.xlong.values) < 5]
    old_u = near_u[near_u.p_year <= r.last_year + 2]
    if len(newer) and len(old_u) == 0:
        rows.append((code, r, near_u, newer))
say(f"  EIA plants with no turbines under their code in USWTDB: {mm.u_turbines.isna().sum()}; "
    f"meeting all conditions: {len(rows)}")
for code, r, near_u, newer in rows:
    names = "; ".join(sorted(set(near_u.p_name.astype(str)))) or "none"
    say(f"    {int(code)} {r['name']} ({r.state}, {int(r.last_year)}): EIA {r.mw:.1f} MW, {r.turbines:.0f} turbines. "
        f"USWTDB within 5 km: {len(near_u)} turbines ({names})")
    for c2, r2 in newer.iterrows():
        say(f"        newer plant {int(c2)} {r2['name']} ({int(r2.first_year)}), {r2.mw:.1f} MW")

# ---------------------------------------------------------------- C: model updated, count not
say("\nC. Plants where USWTDB shows a repowering (all turbines retrofitted) but EIA's turbine count is "
    "at least 1.5 times USWTDB's")
c = m[(m.u_retrofit > 0) & (m.u_retrofit == m.u_turbines) & (m.turbines >= 1.5 * m.u_turbines)]
for code, r in c.iterrows():
    models = "; ".join(sorted(set(w[w["Plant Code"] == code]["Predominant Turbine Model Number"].astype(str))))
    say(f"    {int(code)} {r['name']} ({r.state}): EIA {r.mw:.1f} MW, {r.turbines:.0f} turbines, model {models}; "
        f"USWTDB {r.u_turbines:.0f} turbines listed ({r.u_stated:.0f} stated), {r.u_mw:.1f} MW")

# ---------------------------------------------------------------- D: implausible turbine counts
say("\nD. Generators reporting under 0.3 MW per turbine with a turbine model of 2 MW or more")
model_mw = pd.to_numeric(w["Predominant Turbine Model Number"].astype(str)
                         .str.extract(r"(\d\.\d+)")[0], errors="coerce")
per = w[CAP] / w["Number of Turbines"]
d = w[(per < 0.3) & (model_mw >= 2) & (w["Number of Turbines"] >= 10)]
for _, r in d.iterrows():
    say(f"    {r['Plant Code']} {r['Plant Name']} ({r['State']}) generator {r['Generator ID']}: {r[CAP]:.1f} MW, "
        f"{r['Number of Turbines']:.0f} turbines, model {r['Predominant Turbine Model Number']}")

(HERE / "p30_repower_findings.txt").write_text(out.getvalue(), encoding="utf-8")
print("\nSaved p30_repower_findings.txt")
