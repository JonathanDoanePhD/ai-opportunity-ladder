"""Build task-rating batches from O*NET 30.0 task statements (whole occupations kept together).

python3 -I scripts/01_make_batches.py
  -> data/interim/batches/task/batch_NNNN.jsonl (about 200 tasks each)
  -> data/coded/reliability_batches.txt (5 fixed batches for a reference-model pass)
"""
import json, random
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ONET = ROOT / "data" / "raw" / "onet" / "db_30_0_text"
B = ROOT / "data" / "interim" / "batches" / "task"; B.mkdir(parents=True, exist_ok=True)
TARGET, SEED = 200, 20261125

t = pd.read_csv(ONET / "Task Statements.txt", sep="\t", dtype={"Task ID": str})
occ = pd.read_csv(ONET / "Occupation Data.txt", sep="\t")[["O*NET-SOC Code", "Title"]]
t = t.merge(occ, on="O*NET-SOC Code").sort_values(["O*NET-SOC Code", "Task ID"])
for f in B.glob("batch_*.jsonl"):
    f.unlink()
n, cur = 0, []


def flush(rows):
    global n
    n += 1
    with open(B / f"batch_{n:04d}.jsonl", "w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")


for code, g in t.groupby("O*NET-SOC Code", sort=True):
    rows = [{"id": r["Task ID"], "occupation_code": code, "occupation": r["Title"], "title": r["Title"], "abstract": r["Task"], "task": r["Task"]}
            for _, r in g.iterrows()]
    if cur and len(cur) + len(rows) > TARGET:
        flush(cur); cur = []
    cur += rows
if cur:
    flush(cur)
rel = sorted(random.Random(SEED).sample(range(1, n + 1), 5))
C = ROOT / "data" / "coded"; C.mkdir(parents=True, exist_ok=True)
(C / "reliability_batches.txt").write_text("\n".join(f"batch_{i:04d}" for i in rel) + "\n")
print(f"{len(t):,} tasks, {t['O*NET-SOC Code'].nunique()} occupations, {n} batches; reliability batches {rel}")
