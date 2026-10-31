"""Summaries from raw.jsonl + grades.jsonl. Writes results/summary.json and prints tables."""
import json, random, statistics as st
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
import os
KEY_PATH, RAW_PATH = os.environ.get("KEY", "runner/answer_key.json"), os.environ.get("RAW", "results/raw.jsonl")
GRADES_PATH, SUMMARY_PATH = os.environ.get("GRADES", "results/grades.jsonl"), os.environ.get("SUMMARY", "results/summary.json")
key = {q["qid"]: q for q in json.loads((ROOT / KEY_PATH).read_text())}
raw = {(r["qid"], r["repeat"], r["mode"]): r for r in map(json.loads, (ROOT / RAW_PATH).read_text().splitlines())}
grades = {(g["qid"], g["repeat"], g["mode"]): g for g in map(json.loads, (ROOT / GRADES_PATH).read_text().splitlines())}
assert set(raw) == set(grades), (len(raw), len(grades))
# Manual adjudications of inconsistent judge verdicts, logged with reasons in notes/adjudications.json.
ADJ = ROOT / os.environ.get("ADJ", "notes/adjudications.json")
for a in (json.loads(ADJ.read_text()) if ADJ.exists() else []):
    g = grades[(a["qid"], a["repeat"], a["mode"])]
    for c, v in zip(g["criteria"], a["criteria"]):
        c["pass"] = v
    g["unsupported_claims"] = a.get("unsupported_claims", g["unsupported_claims"])
    g["passed"] = all(a["criteria"])
MODES = ["FLASH", "STANDARD"]
LEVELS = list(dict.fromkeys(q["level"] for q in key.values()))

def pct(xs, p):
    xs = sorted(xs)
    k = (len(xs) - 1) * p
    lo, hi = int(k), min(int(k) + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (k - lo)

rows = []
for k, r in raw.items():
    g = grades[k]
    q = key[k[0]]
    rows.append(dict(qid=k[0], repeat=k[1], mode=k[2], level=q["level"], case=q["case"], version=q["version"],
                     passed=g["passed"], criteria=[c["pass"] for c in g["criteria"]], failed=g["technical_failure"],
                     unsupported=g["unsupported_claims"], sec=r["elapsed_s"], sql=len(r["sql"]), status=r["status"],
                     words=len((r["answer"] or "").split())))

summary = {"n_requests": len(rows), "failures": {m: sum(x["failed"] for x in rows if x["mode"] == m) for m in MODES}}
print("requests", len(rows), "technical failures", summary["failures"])

print("\nPASS RATE (all four criteria)")
summary["pass"] = {}
for lvl in LEVELS + ["all"]:
    line = []
    for m in MODES:
        xs = [x for x in rows if x["mode"] == m and (lvl == "all" or x["level"] == lvl)]
        p = sum(x["passed"] for x in xs)
        summary["pass"].setdefault(lvl, {})[m] = {"passed": p, "n": len(xs)}
        line.append(f"{m} {p}/{len(xs)} ({p / len(xs):.0%})")
    print(f"  {lvl:9s}", " | ".join(line))

print("\nCORRECT CONCLUSION (criterion 4, directed and open)")
summary["conclusion"] = {}
for lvl in ["directed", "open"]:
    line = []
    for m in MODES:
        xs = [x for x in rows if x["mode"] == m and x["level"] == lvl]
        p = sum(x["criteria"][3] for x in xs)
        summary["conclusion"].setdefault(lvl, {})[m] = {"passed": p, "n": len(xs)}
        line.append(f"{m} {p}/{len(xs)} ({p / len(xs):.0%})")
    print(f"  {lvl:9s}", " | ".join(line))

print("\nPASS BY QUESTION (of 5)")
summary["by_question"] = {}
for qid in key:
    f = sum(x["passed"] for x in rows if x["qid"] == qid and x["mode"] == "FLASH")
    s = sum(x["passed"] for x in rows if x["qid"] == qid and x["mode"] == "STANDARD")
    crit = {m: [sum(x["criteria"][i] for x in rows if x["qid"] == qid and x["mode"] == m) for i in range(4)] for m in MODES}
    summary["by_question"][qid] = {"FLASH": f, "STANDARD": s, "criteria": crit}
    print(f"  {qid:30s} Flash {f}  Standard {s}   crit F{crit['FLASH']} S{crit['STANDARD']}")

print("\nPAIRED OUTCOMES (qid, repeat)")
summary["pairs"] = {}
for lvl in LEVELS + ["all"]:
    c = defaultdict(int)
    for qid in key:
        if lvl != "all" and key[qid]["level"] != lvl:
            continue
        for rep in range(1, 6):
            f, s = grades[(qid, rep, "FLASH")]["passed"], grades[(qid, rep, "STANDARD")]["passed"]
            c["both pass" if f and s else "Standard only" if s else "Flash only" if f else "both fail"] += 1
    summary["pairs"][lvl] = dict(c)
    print(f"  {lvl:9s}", dict(c))

print("\nCOMPLETION TIME, completed requests (seconds)")
summary["time"] = {}
for lvl in LEVELS + ["all"]:
    line = []
    for m in MODES:
        xs = [x["sec"] for x in rows if x["mode"] == m and not x["failed"] and (lvl == "all" or x["level"] == lvl)]
        summary["time"].setdefault(lvl, {})[m] = {"median": round(st.median(xs), 1), "p90": round(pct(xs, 0.9), 1), "n": len(xs)}
        line.append(f"{m} median {st.median(xs):.1f} p90 {pct(xs, 0.9):.1f}")
    print(f"  {lvl:9s}", " | ".join(line))

ratios = []
for qid in key:
    for rep in range(1, 6):
        f, s = raw[(qid, rep, "FLASH")], raw[(qid, rep, "STANDARD")]
        if f["status"] == "completed" and s["status"] == "completed":
            ratios.append(s["elapsed_s"] / f["elapsed_s"])
summary["paired_ratio_standard_over_flash"] = {"median": round(st.median(ratios), 2), "p10": round(pct(ratios, 0.1), 2),
                                               "p90": round(pct(ratios, 0.9), 2), "share_standard_slower": round(sum(r > 1 for r in ratios) / len(ratios), 2), "n": len(ratios)}
print("\npaired time ratio Standard/Flash", summary["paired_ratio_standard_over_flash"])

print("\nSQL CALLS, WORDS, UNSUPPORTED CLAIMS")
summary["diagnostics"] = {}
for lvl in LEVELS + ["all"]:
    line = []
    for m in MODES:
        xs = [x for x in rows if x["mode"] == m and (lvl == "all" or x["level"] == lvl)]
        d = {"sql_mean": round(st.mean(x["sql"] for x in xs), 2), "words_median": st.median(x["words"] for x in xs),
             "unsupported_total": sum(x["unsupported"] for x in xs),
             "responses_with_unsupported": sum(x["unsupported"] > 0 for x in xs)}
        summary["diagnostics"].setdefault(lvl, {})[m] = d
        line.append(f"{m} {d}")
    print(f"  {lvl:9s}", " | ".join(line))

# Bootstrap over questions (cluster) for the open-question pass-rate difference.
open_q = [q for q in key if key[q]["level"] == "open"]
rng = random.Random(7)
diffs = []
for _ in range(10000):
    sample = [rng.choice(open_q) for _ in open_q]
    f = sum(summary["by_question"][q]["FLASH"] for q in sample) / (5 * len(sample))
    s = sum(summary["by_question"][q]["STANDARD"] for q in sample) / (5 * len(sample))
    diffs.append(s - f)
summary["open_diff_ci95"] = [round(pct(diffs, 0.025), 3), round(pct(diffs, 0.975), 3)]
print("\nopen pass-rate difference Standard - Flash, 95% question bootstrap", summary["open_diff_ci95"])

(ROOT / SUMMARY_PATH).write_text(json.dumps(summary, indent=1))
