"""Rating reliability (main Sonnet pass vs reference model) and external validation vs Eloundou et al. (2024).

python3 -I scripts/03_reliability.py -> output/rating_reliability.csv, output/external_validation.csv
Ordinal fields use linearly weighted Cohen's kappa. External validation: our ai_speedup = large (or ai_alone >= 2)
vs the human annotators' E1 label (LLM alone can halve task time), at task level (agreement, kappa) and
occupation level (correlation of exposure shares).
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
C, OUT = ROOT / "data" / "coded", ROOT / "output"
OUT.mkdir(exist_ok=True)
SPEED = {"none": 0, "moderate": 1, "large": 2}


def wkappa(a, b, k):
    a, b = np.asarray(a, int), np.asarray(b, int)
    if len(a) == 0:
        return np.nan
    O = np.zeros((k, k))
    for x, y in zip(a, b):
        O[x, y] += 1
    W = np.abs(np.subtract.outer(np.arange(k), np.arange(k))) / (k - 1)
    E = np.outer(O.sum(1), O.sum(0)) / O.sum()
    return 1 - (W * O).sum() / (W * E).sum() if (W * E).sum() else 1.0


def load(p):
    return {str(e["id"]): e for f in sorted((C / p).glob("batch_*.json")) for e in json.loads(f.read_text())}


M, R = load("main"), load("reference")
ids = sorted(set(M) & set(R))
rows = []
for f, k, conv in [("ai_alone", 4, int), ("ai_speedup", 3, SPEED.get), ("human_core", 3, int), ("physical", 3, int)]:
    a = [conv(M[i][f]) for i in ids]; b = [conv(R[i][f]) for i in ids]
    rows.append({"field": f, "n": len(ids), "pct_exact": np.mean([x == y for x, y in zip(a, b)]) if ids else np.nan,
                 "pct_within_1": np.mean([abs(x - y) <= 1 for x, y in zip(a, b)]) if ids else np.nan,
                 "weighted_kappa": wkappa(a, b, k), "mean_main": np.mean(a) if ids else np.nan, "mean_reference": np.mean(b) if ids else np.nan})
pd.DataFrame(rows).to_csv(OUT / "rating_reliability.csv", index=False, float_format="%.3f")
print(pd.DataFrame(rows).round(3).to_string(index=False))

# external validation
g = pd.read_csv(ROOT / "data" / "raw" / "gpts" / "full_labelset.tsv", sep="\t")
g["id"] = g["Task ID"].astype("Int64").astype(str)
g["human_e1"] = g.human_exposure_agg.eq("E1"); g["human_e1e2"] = g.human_exposure_agg.isin(["E1", "E2"])
mine = pd.DataFrame([{"id": i, "large": M[i]["ai_speedup"] == "large", "capable": M[i]["ai_alone"] >= 2, "occ": None} for i in M])
v = mine.merge(g[["id", "O*NET-SOC Code", "human_e1", "human_e1e2"]], on="id")


def kap(a, b):
    a, b = np.asarray(a), np.asarray(b); po = (a == b).mean(); pe = a.mean() * b.mean() + (1 - a.mean()) * (1 - b.mean())
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


ext = []
for ours in ["large", "capable"]:
    for theirs in ["human_e1", "human_e1e2"]:
        occ = v.groupby("O*NET-SOC Code")[[ours, theirs]].mean()
        ext.append({"ours": ours, "theirs": theirs, "tasks": len(v), "share_ours": v[ours].mean(), "share_theirs": v[theirs].mean(),
                    "task_agreement": (v[ours] == v[theirs]).mean(), "task_kappa": kap(v[ours], v[theirs]),
                    "occupations": len(occ), "occ_corr_pearson": occ[ours].corr(occ[theirs]), "occ_corr_spearman": occ[ours].corr(occ[theirs], method="spearman")})
pd.DataFrame(ext).to_csv(OUT / "external_validation.csv", index=False, float_format="%.3f")
print(pd.DataFrame(ext).round(3).to_string(index=False))
