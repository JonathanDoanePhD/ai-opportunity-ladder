"""Progress and pending batches (done = output exists AND validates).

python3 -I scripts/status.py [--json]
"""
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
B, C = ROOT / "data" / "interim" / "batches" / "task", ROOT / "data" / "coded"


def valid(out):
    return out.exists() and subprocess.run([sys.executable, "-I", str(ROOT / "scripts" / "validate.py"), str(out)], capture_output=True).returncode == 0


bs = [b.stem for b in sorted(B.glob("batch_*.jsonl"))]
rel = (C / "reliability_batches.txt").read_text().split() if (C / "reliability_batches.txt").exists() else []
s = {"main_pending": [b for b in bs if not valid(C / "main" / f"{b}.json")], "main_total": len(bs),
     "reference_pending": [b for b in rel if not valid(C / "reference" / f"{b}.json")], "reference_total": len(rel)}
if "--json" in sys.argv:
    print(json.dumps(s))
else:
    print(f"main      {s['main_total'] - len(s['main_pending'])}/{s['main_total']} batches done")
    print(f"reference {s['reference_total'] - len(s['reference_pending'])}/{s['reference_total']} batches done")
