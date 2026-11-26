"""AI and the Opportunity Ladder: occupation AI profiles, pathways without a bachelor's, county exposure, programs.

python3 -I scripts/04_analysis.py   (works with partial ratings)
Outputs (output/):
  occupation_ai_profile.csv    one row per rated occupation: AI shares, category, education, earnings, employment
  exposure_by_education.csv    employment-weighted AI profile by typical required education
  pathways_no_ba.csv           occupations typically entered without a bachelor's that pay at least the national median
                               (full-time), ranked by how human-anchored they are
  county_exposure.csv          per county: employment-weighted AI shares from its occupation mix (ACS C24010), priority flag
  programs_to_pathways.csv     certificate and associate programs (Scorecard) linked to pathway occupations, with Pell earnings
  ladder_summary.json          headline numbers
  fig_earnings_vs_ai.png, fig_county_exposure.png
Definitions (task importance-weighted shares):
  ai_can_do    tasks rated ai_alone >= 2 (AI can do most of the task)
  ai_speeds    tasks rated ai_alone <= 1 with moderate or large speedup (a person still does it, faster with AI)
  anchored     tasks rated ai_alone <= 1 and human_core = 2 or physical = 2 (rests on relationships or presence)
  category     "AI can do much of it" if ai_can_do >= 0.5; "Human-anchored" if anchored >= 0.5; else "AI-augmented / mixed"
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW, INT, C, OUT = ROOT / "data" / "raw", ROOT / "data" / "interim", ROOT / "data" / "coded", ROOT / "output"
ONET = RAW / "onet" / "db_30_0_text"
OUT.mkdir(exist_ok=True)
summary = {}

# ---------- task ratings + importance weights ----------
rat = pd.DataFrame([e for f in sorted((C / "main").glob("batch_*.json")) for e in json.loads(f.read_text())])
rat["id"] = rat.id.astype(str)
ts = pd.read_csv(ONET / "Task Statements.txt", sep="\t", dtype={"Task ID": str})[["O*NET-SOC Code", "Task ID", "Task Type"]]
ts.columns = ["onet", "id", "task_type"]
im = pd.read_csv(ONET / "Task Ratings.txt", sep="\t", dtype={"Task ID": str})
im = im[im["Scale ID"] == "IM"][["O*NET-SOC Code", "Task ID", "Data Value"]]; im.columns = ["onet", "id", "importance"]
t = rat.merge(ts, on="id").merge(im, on=["onet", "id"], how="left")
t["w"] = t.importance.fillna(t.importance.median() if t.importance.notna().any() else 4.0)
t["can"] = t.ai_alone >= 2
t["speeds"] = (t.ai_alone <= 1) & t.ai_speedup.isin(["moderate", "large"])
t["anchored"] = (t.ai_alone <= 1) & ((t.human_core == 2) | (t.physical == 2))
summary["tasks_rated"] = int(len(t))


def wavg(g, col):
    return np.average(g[col].astype(float), weights=g.w)


prof = t.groupby("onet").apply(lambda g: pd.Series({
    "tasks": len(g), "ai_can_do": wavg(g, "can"), "ai_full": wavg(g.assign(f=g.ai_alone == 3), "f"), "ai_speeds": wavg(g, "speeds"),
    "anchored": wavg(g, "anchored"), "human_core_mean": wavg(g, "human_core"), "physical_mean": wavg(g, "physical"),
    "large_speedup": wavg(g.assign(f=g.ai_speedup == "large"), "f")}), include_groups=False).reset_index()
prof["category"] = np.where(prof.ai_can_do >= 0.5, "AI can do much of it", np.where(prof.anchored >= 0.5, "Human-anchored", "AI-augmented / mixed"))
occ = pd.read_csv(INT / "occupations.csv")
p = prof.merge(occ, on="onet", how="left")
median_all = float(occ.median_earnings_all_ft.dropna().iloc[0]) if occ.median_earnings_all_ft.notna().any() else np.nan
p["no_ba_entry"] = (p.share_ba_plus < 0.5) & ~p.typical_education.isin(["bachelor", "post_bacc_certificate", "master", "post_master_certificate",
                                                                         "first_professional", "doctoral", "post_doctoral"])
p["pays_median_plus"] = p.median_earnings_ft >= median_all
p.to_csv(OUT / "occupation_ai_profile.csv", index=False, float_format="%.4f")
summary["occupations_rated"] = int(len(p)); summary["national_median_ft_earnings"] = median_all

# ---------- by education ----------
EDU_ORDER = ["less_than_hs", "high_school", "postsecondary_certificate", "some_college", "associate", "bachelor", "master", "doctoral", "post_doctoral",
             "first_professional"]
pe = p.dropna(subset=["employment_est"])
eb = []
for e, g in pe.groupby("typical_education"):
    w = g.employment_est
    eb.append({"typical_education": e, "occupations": len(g), "employment": w.sum(),
               **{k: np.average(g[k], weights=w) for k in ["ai_can_do", "ai_speeds", "anchored"]},
               "share_jobs_ai_can_do_cat": w[g.category == "AI can do much of it"].sum() / w.sum(),
               "share_jobs_anchored_cat": w[g.category == "Human-anchored"].sum() / w.sum(),
               "median_earnings_weighted": np.average(g.median_earnings_ft.fillna(g.median_earnings_ft.median()), weights=w)})
ebd = pd.DataFrame(eb); ebd["order"] = ebd.typical_education.map({e: i for i, e in enumerate(EDU_ORDER)}); ebd = ebd.sort_values("order").drop(columns="order")
ebd.to_csv(OUT / "exposure_by_education.csv", index=False, float_format="%.4f")
if len(pe):
    w = pe.employment_est
    summary["jobs"] = {
        "employment_covered": float(w.sum()),
        "share_jobs_by_category": {c: float(w[pe.category == c].sum() / w.sum()) for c in pe.category.unique()},
        "no_ba": {c: float(pe[pe.no_ba_entry & (pe.category == c)].employment_est.sum() / pe[pe.no_ba_entry].employment_est.sum()) for c in pe.category.unique()},
        "ba_plus": {c: float(pe[~pe.no_ba_entry & (pe.category == c)].employment_est.sum() / pe[~pe.no_ba_entry].employment_est.sum()) for c in pe.category.unique()},
        "corr_earnings_ai_can_do": float(pe[["median_earnings_ft", "ai_can_do"]].corr().iloc[0, 1]),
    }

# ---------- pathways without a bachelor's ----------
pw = p[p.no_ba_entry & p.pays_median_plus].copy()
pw["resilience"] = pw.anchored - pw.ai_can_do
cols = ["onet", "title", "typical_education", "job_zone", "median_earnings_ft", "employment_est", "census_occ_shared_by", "category", "ai_can_do", "ai_speeds", "anchored",
        "human_core_mean", "physical_mean", "county_group"]
pw.sort_values(["resilience", "median_earnings_ft"], ascending=False)[cols + ["resilience"]].to_csv(OUT / "pathways_no_ba.csv", index=False, float_format="%.4f")
summary["pathways_no_ba"] = {"occupations": int(len(pw)), "employment": float(pw.employment_est.sum()),
                             "by_category": {c: int((pw.category == c).sum()) for c in pw.category.unique()},
                             "employment_by_category": {c: float(pw[pw.category == c].employment_est.sum()) for c in pw.category.unique()}}

# ---------- county exposure from C24010 ----------
grp = pe.groupby("county_group").apply(lambda g: pd.Series({k: np.average(g[k], weights=g.employment_est) for k in ["ai_can_do", "ai_speeds", "anchored"]}),
                                        include_groups=False)
sh = pd.read_csv(RAW / "acs" / "ACS20231YR_Table_Shells.txt", sep="|", dtype=str)
lab = sh[sh["Table ID"] == "C24010"].set_index("Unique ID").Label.str.replace(" occupations", "", regex=False).str.rstrip(":").str.strip()
cd = pd.read_csv(RAW / "acs" / "acsdt5y2023-c24010.dat", sep="|", dtype=str)
cd = cd[cd.GEO_ID.str.startswith("0500000US")].copy()
cd["fips"] = cd.GEO_ID.str[-5:]
leaf = {}
for uid, l in lab.items():
    if l in grp.index:
        leaf.setdefault(l, []).append(uid.replace("_", "_E"))
rows = []
for _, r in cd.iterrows():
    jobs = {g: sum(pd.to_numeric(r.get(c), errors="coerce") or 0 for c in cs) for g, cs in leaf.items()}
    tot = sum(jobs.values())
    if not tot:
        continue
    rows.append({"fips": r.fips, "jobs": tot, **{k: sum(jobs[g] * grp.loc[g, k] for g in jobs) / tot for k in ["ai_can_do", "ai_speeds", "anchored"]},
                 "share_office_admin": jobs.get("Office and administrative support", 0) / tot, "share_sales": jobs.get("Sales and related", 0) / tot})
ce = pd.DataFrame(rows)
ct = pd.read_csv(ROOT / "data" / "external" / "county_table_project01.csv", dtype={"fips": str})
ct["fips"] = ct.fips.str.zfill(5)
ce = ce.merge(ct[["fips", "county_name", "state", "priority_flag", "need_index", "mobility_p25_income_rank"]], on="fips", how="left")
ce.to_csv(OUT / "county_exposure.csv", index=False, float_format="%.4f")
if len(ce):
    pr = ce[ce.priority_flag == True]; ot = ce[ce.priority_flag != True]
    summary["counties"] = {"counties": int(len(ce)),
                           "priority_mean": {k: float(np.average(pr[k], weights=pr.jobs)) for k in ["ai_can_do", "ai_speeds", "anchored"]} if len(pr) else None,
                           "other_mean": {k: float(np.average(ot[k], weights=ot.jobs)) for k in ["ai_can_do", "ai_speeds", "anchored"]},
                           "corr_need_ai_can_do": float(ce[["need_index", "ai_can_do"]].corr().iloc[0, 1]),
                           "corr_mobility_ai_can_do": float(ce[["mobility_p25_income_rank", "ai_can_do"]].corr().iloc[0, 1])}

# ---------- programs (certificates, associate) -> pathway occupations ----------
sc = pd.read_csv(RAW / "scorecard" / "Most-Recent-Cohorts-Field-of-Study.csv", dtype=str,
                 usecols=["CIPCODE", "CIPDESC", "CREDLEV", "CREDDESC", "EARN_MDN_5YR_NAT", "EARN_MDN_PELL_5YR_NAT", "UNITID"])
sc = sc[sc.CREDLEV.isin(["1", "2"])]
prog = sc.groupby(["CIPCODE", "CIPDESC", "CREDDESC"]).agg(institutions=("UNITID", "nunique"),
                                                         earn_5yr_nat=("EARN_MDN_5YR_NAT", lambda x: pd.to_numeric(x, errors="coerce").median()),
                                                         earn_pell_5yr_nat=("EARN_MDN_PELL_5YR_NAT", lambda x: pd.to_numeric(x, errors="coerce").median())).reset_index()
cw = pd.read_excel(RAW / "nces" / "CIP2020_SOC2018_Crosswalk.xlsx", sheet_name="CIP-SOC", dtype=str)
cw["cip4"] = cw.CIP2020Code.str.replace(".", "", regex=False).str.zfill(6).str[:4]
cw["soc"] = cw.SOC2018Code.str.strip()
p["soc"] = p.onet.str[:7]
socp = p.groupby("soc").agg(ai_can_do=("ai_can_do", "mean"), anchored=("anchored", "mean"), median_earnings_ft=("median_earnings_ft", "max"),
                            no_ba_entry=("no_ba_entry", "max"), category=("category", lambda x: x.mode().iat[0])).reset_index()
link = cw.merge(socp, on="soc")
pl = prog.merge(link.groupby("cip4").agg(target_occupations=("soc", "nunique"), target_ai_can_do=("ai_can_do", "mean"),
                                        target_anchored=("anchored", "mean"), target_median_earnings=("median_earnings_ft", "median")).reset_index(),
                left_on="CIPCODE", right_on="cip4", how="inner").drop(columns="cip4")
pl["pathway_score"] = pl.target_anchored - pl.target_ai_can_do
pl.sort_values(["pathway_score", "earn_pell_5yr_nat"], ascending=False).to_csv(OUT / "programs_to_pathways.csv", index=False, float_format="%.4f")
summary["programs_linked"] = int(len(pl))

# ---------- figures ----------
if len(pe) > 20:
    fig, ax = plt.subplots(figsize=(10, 6.2), dpi=100)
    for nb, col, labl in [(False, "#c3c2bd", "Typically needs a bachelor's or more"), (True, "#2a78d6", "Typically entered without a bachelor's")]:
        g = pe[pe.no_ba_entry == nb]
        ax.scatter(g.ai_can_do * 100, g.median_earnings_ft / 1000, s=np.clip(g.employment_est / 15000, 6, 260), color=col, alpha=0.55, label=labl, edgecolors="none")
    ax.axhline(median_all / 1000, color="#52514e", lw=0.8, ls="--"); ax.text(99, median_all / 1000 + 2, "national median (full-time)", ha="right", fontsize=8, color="#52514e")
    ax.set_xlabel("Share of the job's tasks that AI can mostly do alone (importance-weighted, %)"); ax.set_ylabel("Median earnings, full-time ($ thousands)")
    ax.set_title("AI capability vs. pay across occupations (dot size = employment)", loc="left", fontsize=12); ax.legend(frameon=False, fontsize=9, loc="upper right")
    fig.text(0.01, 0.01, "Task ratings by AI agents (O*NET 30.0 tasks); earnings ACS 2023. Capability is not the same as job loss. Verify before external use.",
             fontsize=7.5, color="#52514e")
    fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig(OUT / "fig_earnings_vs_ai.png", dpi=150); plt.close(fig)
if len(ce) > 100:
    fig, ax = plt.subplots(figsize=(9.5, 5), dpi=100)
    ax.hist(ce[ce.priority_flag != True].ai_can_do * 100, bins=40, color="#c3c2bd", density=True, label="Other counties")
    ax.hist(ce[ce.priority_flag == True].ai_can_do * 100, bins=25, color="#eb6834", alpha=0.75, density=True, label="Project 01 priority counties")
    ax.set_xlabel("Job-weighted share of local work tasks AI can mostly do alone (%)"); ax.set_ylabel("Density"); ax.legend(frameon=False)
    ax.set_title("How exposed is local work to AI? Counties by occupation mix", loc="left", fontsize=12)
    fig.text(0.01, 0.01, "County occupation mix: ACS 2019-23 (C24010, 25 groups). Verify before external use.", fontsize=7.5, color="#52514e")
    fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig(OUT / "fig_county_exposure.png", dpi=150); plt.close(fig)

(OUT / "ladder_summary.json").write_text(json.dumps(summary, indent=2, default=float))
print(json.dumps(summary, indent=1, default=float))
