"""Occupation reference table: O*NET education and job zone + ACS earnings and employment + county-mix group.

python3 -I scripts/02_build_occupations.py -> data/interim/occupations.csv, output/occupation_match_report.csv
- Education: O*NET "Required Level of Education" (RL) distribution: share of workers in jobs needing a
  bachelor's degree or more, and the most common required level.
- Earnings and employment: ACS 2023 1-year national tables B24121 (median earnings, full-time year-round)
  and B24114 (employment), by Census occupation, linked to SOC through the Census 2018 crosswalk.
  Where one Census occupation covers several O*NET occupations, they share its median earnings and
  split its employment evenly (an approximation used only for weighting).
- County-mix group: the ACS C24010 occupation group each SOC code falls in.
"""
import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW, INT, OUT = ROOT / "data" / "raw", ROOT / "data" / "interim", ROOT / "output"
INT.mkdir(parents=True, exist_ok=True); OUT.mkdir(exist_ok=True)
ONET = RAW / "onet" / "db_30_0_text"

occ = pd.read_csv(ONET / "Occupation Data.txt", sep="\t")[["O*NET-SOC Code", "Title"]].rename(columns={"O*NET-SOC Code": "onet", "Title": "title"})
occ["soc"] = occ.onet.str[:7]

# --- education (RL) and job zone ---
ete = pd.read_csv(ONET / "Education, Training, and Experience.txt", sep="\t")
rl = ete[ete["Element ID"].eq("2.D.1") & ete["Scale ID"].eq("RL")][["O*NET-SOC Code", "Category", "Data Value"]]
rl.columns = ["onet", "cat", "pct"]
LEVEL = {1: "less_than_hs", 2: "high_school", 3: "postsecondary_certificate", 4: "some_college", 5: "associate", 6: "bachelor",
         7: "post_bacc_certificate", 8: "master", 9: "post_master_certificate", 10: "first_professional", 11: "doctoral", 12: "post_doctoral"}
edu = rl.groupby("onet").apply(lambda g: pd.Series({
    "share_ba_plus": g[g.cat >= 6].pct.sum() / 100, "typical_education": LEVEL.get(int(g.loc[g.pct.idxmax(), "cat"]), "unknown")}),
    include_groups=False).reset_index()
jz = pd.read_csv(ONET / "Job Zones.txt", sep="\t")[["O*NET-SOC Code", "Job Zone"]].rename(columns={"O*NET-SOC Code": "onet", "Job Zone": "job_zone"})
occ = occ.merge(edu, on="onet", how="left").merge(jz, on="onet", how="left")

# --- Census occupation list (title, code, SOC pattern) ---
cl = pd.read_excel(RAW / "census" / "2018-occupation-code-list-and-crosswalk.xlsx", sheet_name="2018 Census Occ Code List", header=None)
cl = cl.iloc[:, 1:4]; cl.columns = ["ctitle", "ccode", "csoc"]
cl = cl[cl.ccode.astype(str).str.fullmatch(r"\d{4}") & cl.csoc.notna()].copy()
cl["ccode"] = cl.ccode.astype(str); cl["csoc"] = cl.csoc.astype(str).str.strip()
norm = lambda s: re.sub(r"[^a-z0-9]+", " ", str(s).lower()).strip()
cl["key"] = cl.ctitle.map(norm)

# --- ACS lines -> Census titles ---
sh = pd.read_csv(RAW / "acs" / "ACS20231YR_Table_Shells.txt", sep="|", dtype=str)


def acs_table(tid, fname):
    s = sh[(sh["Table ID"] == tid) & (sh["Unique ID"] != f"{tid}_001")][["Unique ID", "Label"]]
    d = pd.read_csv(RAW / "acs" / fname, sep="|", dtype=str)
    row = d[d.GEO_ID.str.startswith("0100000US")].iloc[0]
    s["value"] = s["Unique ID"].map(lambda u: pd.to_numeric(row.get(u.replace("_", "_E")), errors="coerce"))
    s["key"] = s.Label.map(norm)
    total = pd.to_numeric(row.get(f"{tid}_E001"), errors="coerce")
    return s, total


earn, median_all = acs_table("B24121", "acsdt1y2023-b24121.dat")
emp, emp_all = acs_table("B24114", "acsdt1y2023-b24114.dat")
cl = cl.merge(earn[["key", "value"]].rename(columns={"value": "median_earnings_ft"}), on="key", how="left")
cl = cl.merge(emp[["key", "value"]].rename(columns={"value": "employment_census_occ"}), on="key", how="left")


def soc_match(soc, pattern):
    pat = pattern.replace("X", ".")
    return re.fullmatch(pat, soc) is not None


# each O*NET SOC -> the Census occupation whose SOC pattern matches (exact first, then wildcard)
exact = dict(zip(cl.csoc, cl.index))
wild = cl[cl.csoc.str.contains("X")]
assign = {}
for soc in occ.soc.unique():
    if soc in exact:
        assign[soc] = exact[soc]
    else:
        m = [i for i, p in zip(wild.index, wild.csoc) if soc_match(soc, p)]
        if not m:  # Census broad codes ending in 0 (e.g. 11-2030 covers 11-2032 and 11-2033), then 5-digit, then minor-group
            m = [i for i, p in zip(cl.index, cl.csoc) if p.endswith("0") and soc.startswith(p[:6])]
        if not m:
            m = [i for i, p in zip(cl.index, cl.csoc) if p.endswith("00") and soc.startswith(p[:5])]
        if m:
            assign[soc] = m[0]
occ["census_idx"] = occ.soc.map(assign)
occ = occ.merge(cl[["ctitle", "ccode", "median_earnings_ft", "employment_census_occ"]], left_on="census_idx", right_index=True, how="left")
n_share = occ.groupby("ccode").onet.transform("count")
occ["employment_est"] = occ.employment_census_occ / n_share
occ["census_occ_shared_by"] = n_share  # >1: employment is an even split of a Census occupation group (approximate)


# --- county-mix (C24010) group ---
def c24010_group(soc):
    mj, minor = soc[:2], soc[:4]
    m = {"11": "Management", "13": "Business and financial operations", "15": "Computer and mathematical", "17": "Architecture and engineering",
         "19": "Life, physical, and social science", "21": "Community and social service", "23": "Legal", "25": "Educational instruction, and library",
         "27": "Arts, design, entertainment, sports, and media", "31": "Healthcare support", "35": "Food preparation and serving related",
         "37": "Building and grounds cleaning and maintenance", "39": "Personal care and service", "41": "Sales and related",
         "43": "Office and administrative support", "45": "Farming, fishing, and forestry", "47": "Construction and extraction",
         "49": "Installation, maintenance, and repair", "51": "Production"}
    if mj == "29":
        return "Health technologists and technicians" if minor == "29-2" else "Health diagnosing and treating practitioners and other technical"
    if mj == "33":
        return "Law enforcement workers including supervisors" if (minor == "33-3" or soc == "33-1012") else "Firefighting and prevention, and other protective service workers including supervisors"
    if mj == "53":
        return "Material moving" if minor == "53-7" else "Transportation"
    return m.get(mj, "Other")


occ["county_group"] = occ.soc.map(c24010_group)
occ["median_earnings_all_ft"] = median_all
occ = occ.drop(columns=["census_idx"])
occ.to_csv(INT / "occupations.csv", index=False)
rep = pd.DataFrame([{"onet_occupations": len(occ), "with_education": int(occ.share_ba_plus.notna().sum()), "with_job_zone": int(occ.job_zone.notna().sum()),
                     "matched_census_occ": int(occ.ccode.notna().sum()), "with_median_earnings": int(occ.median_earnings_ft.notna().sum()),
                     "with_employment": int(occ.employment_est.notna().sum()), "acs_lines_matched_earnings": int(cl.median_earnings_ft.notna().sum()),
                     "acs_lines_total": len(earn), "national_median_earnings_ft": median_all, "national_employment": emp_all}])
rep.to_csv(OUT / "occupation_match_report.csv", index=False)
print(rep.T.to_string())
