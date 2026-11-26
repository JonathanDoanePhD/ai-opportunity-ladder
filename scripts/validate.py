"""Validate a task-rating file against docs/protocol.md. Exit code 0 = valid.

python3 -I scripts/validate.py data/coded/main/batch_0001.json
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STOPW = set("the a an of and or for in on to with by from at as is are was were be this that these those not no other "
            "such including using use work workers ensure".split())


def alignment(inp, out):
    w = lambda t: {x[:6] for x in re.findall(r"[a-z]{4,}", str(t).lower()) if x not in STOPW}
    tx = [w(r["task"]) for r in inp]
    wins = n = 0
    for i, r in enumerate(inp):
        rw = w(out.get(r["id"], {}).get("notes", ""))
        if len(rw) < 1:
            continue
        nbrs = [j for j in (i - 1, i + 1) if 0 <= j < len(inp)]
        own = len(rw & tx[i]); nb = max(len(rw & tx[j]) for j in nbrs)
        n += 1; wins += 1 if own > nb else (0.5 if own == nb and own > 0 else 0)
    return wins / n if n else 1.0


def main(path):
    try:
        data = json.loads(Path(path).read_text())
    except Exception as ex:
        print(f"INVALID JSON: {ex}"); return 1
    if not isinstance(data, list):
        print("INVALID: top level must be a list"); return 1
    inp = [json.loads(l) for l in open(ROOT / "data" / "interim" / "batches" / "task" / f"{Path(path).stem}.jsonl")]
    expected = [r["id"] for r in inp]; got = [str(e.get("id")) for e in data]
    errs = []
    if sorted(got) != sorted(expected):
        m, x = set(expected) - set(got), set(got) - set(expected)
        errs.append(f"id mismatch: missing {sorted(m)[:5]} ({len(m)}), extra {sorted(x)[:5]} ({len(x)}), dupes {len(got) - len(set(got))}")
    for i, e in enumerate(data):
        if e.get("ai_alone") not in (0, 1, 2, 3): errs.append(f"[{i}] ai_alone must be 0-3")
        if e.get("ai_speedup") not in ("none", "moderate", "large"): errs.append(f"[{i}] bad ai_speedup {e.get('ai_speedup')!r}")
        if e.get("human_core") not in (0, 1, 2): errs.append(f"[{i}] human_core must be 0-2")
        if e.get("physical") not in (0, 1, 2): errs.append(f"[{i}] physical must be 0-2")
        if not str(e.get("notes") or "").strip() or len(str(e.get("notes")).split()) > 10: errs.append(f"[{i}] notes must be 1-8 words")
    if not errs:
        a = alignment(inp, {str(e["id"]): e for e in data})
        if a < 0.7:
            errs.append(f"notes do not match their tasks (alignment {a:.2f} < 0.70): ratings look shifted. "
                        "Rebuild the file by matching each task's id to its own text.")
    if errs:
        print("INVALID:\n" + "\n".join(errs[:40])); return 1
    print(f"VALID: {len(data)} records"); return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
