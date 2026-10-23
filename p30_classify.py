"""P30 step 2: group neighbouring plant codes and classify every real disagreement.

Usage (from the P30 folder, after p30_wind_check.py):
    py p30_classify.py
Plant codes are grouped when an EIA plant lies within 10 km of the median of another
code's turbines, so a wind farm filed under several codes is compared as one. Each group
that still disagrees by more than 10% and 5 MW is classified:

  recent build         EIA's first unit entered service in 2025 and USWTDB lists fewer
                       turbines than its own stated count (aerial imagery lags construction)
  turbines missing     USWTDB's project fields (turbine count, capacity) agree with EIA
                       within 10%, but fewer turbines are listed than the project's count
  code assignment      the group's capacity is in one source only, and a plant of a similar
                       name with the capacity exists under a different code elsewhere
  in USWTDB without a plant code
                       EIA only, but USWTDB has turbines with no plant code nearby
  retired / proposed   USWTDB only, and EIA lists the code as retired, cancelled or proposed
  capacity differs     every turbine listed, but the capacities disagree (one source wrong,
                       or a repowering recorded differently)
  unexplained          none of the above

Writes p30_groups.csv and appends a summary to p30_findings.txt.
"""
import difflib
import re
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
TOL, MIN_MW, LINK_KM = 0.10, 5.0, 10.0


def km(lat1, lon1, lat2, lon2):
    p1, p2 = np.radians(lat1), np.radians(lat2)
    a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(np.radians(lon2 - lon1) / 2) ** 2
    return 6371.0 * 2 * np.arcsin(np.sqrt(a))


def simple(name):
    name = re.sub(r"\b(llc|lp|inc|wind|energy|farm|project|center|centre|power|repower(ing)?)\b", " ",
                  str(name).lower())
    return re.sub(r"[^a-z0-9]+", " ", name).strip()


import glob
import io
import zipfile

z = glob.glob(str(HERE.parent / "WY-Grid-Map" / "eia860*.zip"))[0]
with zipfile.ZipFile(z) as zf:
    xl = pd.ExcelFile(io.BytesIO(zf.read(next(n for n in zf.namelist() if n.startswith("3_1_Generator")))))
status_sheets = {}
for sheet, label in (("Retired and Canceled", "retired or cancelled in EIA"), ("Proposed", "proposed, not yet operating, in EIA")):
    df = pd.read_excel(xl, sheet, header=1)
    df = df[df.Technology.str.contains("Wind", na=False)]
    for code in pd.to_numeric(df["Plant Code"], errors="coerce").dropna().astype(int):
        status_sheets.setdefault(code, label)

b = pd.read_csv(HERE / "p30_plants.csv")
for c in ("Latitude", "Longitude", "usw_lat", "usw_lon"):
    b[c] = pd.to_numeric(b[c], errors="coerce")
u = pd.read_csv(sorted(HERE.glob("uswtdb_*.csv"))[-1], dtype={"eia_id": str})
u["eia_id"] = pd.to_numeric(u.eia_id, errors="coerce")
u = u[(u.p_year <= 2025) & (u.t_offshore == 0)]
no_code = u[u.eia_id.isna()]

# USWTDB's own project fields, per plant code
proj = (u.dropna(subset=["eia_id"]).groupby(["eia_id", "p_name"])
        .agg(listed=("case_id", "size"), p_tnum=("p_tnum", "first"), p_cap=("p_cap", "first"))
        .groupby("eia_id").sum(numeric_only=True))

# group codes
g = nx.Graph()
g.add_nodes_from(b.eia_plant_code)
E = b.dropna(subset=["eia_mw", "Latitude"])
U = b.dropna(subset=["usw_turbines", "usw_lat"])
for _, e in E.iterrows():
    d = km(e.Latitude, e.Longitude, U.usw_lat.values, U.usw_lon.values)
    for code in U.eia_plant_code.values[d < LINK_KM]:
        g.add_edge(e.eia_plant_code, code)
group = {n: i for i, comp in enumerate(nx.connected_components(g)) for n in comp}
b["group"] = b.eia_plant_code.map(group)
b = b.join(proj, on="eia_plant_code")

rows = []
eia_names = {simple(n): c for c, n in zip(b.eia_plant_code, b.eia_name) if isinstance(n, str)}
usw_names = {simple(n): c for c, ns in zip(b.eia_plant_code, b.usw_names) if isinstance(ns, str)
             for n in ns.split("; ")}
for gid, grp in b.groupby("group"):
    eia_mw = grp.eia_mw.sum()
    usw_mw = grp.usw_mw.sum()
    if grp.usw_cap_missing.fillna(0).sum() > 0:
        continue
    if abs(usw_mw - eia_mw) <= max(MIN_MW, TOL * max(eia_mw, usw_mw)):
        continue
    listed, tnum, pcap = grp.listed.sum(), grp.p_tnum.sum(), grp.p_cap.sum()
    first_year = pd.to_numeric(grp.eia_first_year, errors="coerce").max()
    names = "; ".join(sorted({str(n) for n in grp.eia_name.dropna()} | {str(n) for n in grp.usw_names.dropna()}))
    if eia_mw > 0 and usw_mw > 0 and listed < tnum and first_year >= 2025:
        kind = "recent build"
    elif eia_mw > 0 and usw_mw > 0 and listed < tnum and abs(pcap - eia_mw) <= TOL * eia_mw:
        kind = "turbines missing"
    elif eia_mw == 0 or usw_mw == 0:
        pool = usw_names if usw_mw == 0 else eia_names
        own = [simple(n) for n in names.split("; ")]
        hits = {pool[m] for n in own for m in difflib.get_close_matches(n, list(pool), n=2, cutoff=0.8)}
        hits -= set(grp.eia_plant_code)
        if hits:
            kind = f"code assignment (see {', '.join(str(int(h)) for h in sorted(hits))})"
        elif usw_mw == 0:
            e = grp.dropna(subset=["Latitude"])
            near = 0
            if len(e):
                d = km(e.Latitude.iloc[0], e.Longitude.iloc[0], no_code.ylat.values, no_code.xlong.values)
                near = int((d < LINK_KM).sum())
            kind = f"in USWTDB without a plant code ({near} turbines within {LINK_KM:.0f} km)" if near else "unexplained"
        else:
            labels = {status_sheets.get(int(c)) for c in grp.eia_plant_code} - {None}
            kind = labels.pop() if labels else "unexplained"
    elif listed >= tnum:
        kind = "capacity differs"
    else:
        kind = "unexplained"
    rows.append({"group": gid, "codes": ";".join(str(int(c)) for c in grp.eia_plant_code),
                 "state": ";".join(sorted({s for s in grp.eia_state.dropna()} |
                                          {s for ss in grp.usw_state.dropna() for s in ss.split(";")})),
                 "names": names, "eia_mw": round(eia_mw, 1), "usw_mw": round(usw_mw, 1),
                 "diff_mw": round(usw_mw - eia_mw, 1), "turbines_listed": int(listed),
                 "usw_stated_turbines": int(tnum), "usw_stated_mw": round(pcap, 1),
                 "eia_latest_first_year": first_year, "kind": kind})

out = pd.DataFrame(rows).sort_values("diff_mw")
# a group named by another group's code assignment is the other half of the same mix-up
seen = {c for k in out.kind if k.startswith("code assignment") for c in re.findall(r"\d+", k)}
partner = out.codes.str.split(";").apply(lambda cs: bool(set(cs) & seen)) & (out.kind == "unexplained")
out.loc[partner, "kind"] = "code assignment (counterpart)"
out.to_csv(HERE / "p30_groups.csv", index=False)
kinds = out.kind.str.replace(r" \(.*\)", "", regex=True)
lines = ["", "6. Groups of neighbouring codes that still disagree, by kind",
         f"  groups compared: {b.group.nunique()}; disagreeing: {len(out)}"]
for k, sub in out.groupby(kinds):
    lines.append(f"    {k}: {len(sub)} groups, net {sub.diff_mw.sum():+,.0f} MW (USWTDB minus EIA)")
text = "\n".join(lines)
print(text)
pd.set_option("display.width", 220)
print(out[["codes", "state", "names", "eia_mw", "usw_mw", "turbines_listed", "usw_stated_turbines", "kind"]]
      .to_string(index=False, max_colwidth=40))
with open(HERE / "p30_findings.txt", "a", encoding="utf-8") as f:
    f.write(text + "\n")
