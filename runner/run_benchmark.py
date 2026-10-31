"""Run 28 questions x 5 repeats x 2 modes = 280 requests in 140 pairs.
Pair order and mode order within each pair are randomized with a fixed seed.
Each request starts a fresh conversation. Nothing is retried; failures stay in the record.
Records append to results/raw.jsonl, so a rerun skips completed (qid, repeat, mode) keys."""
import json, os, random, sys, threading, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from genie_call import ask, SPACE_ID

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / os.environ.get("RAW", "results/raw.jsonl")
# Round 2 routes each question to its agent: GENIE_SPACE_R2 and GENIE_SPACE_NODEFS.
SPACES = {"r2": os.environ.get("GENIE_SPACE_R2"), "nodefs": os.environ.get("GENIE_SPACE_NODEFS")}
REPEATS, WORKERS, SEED = 5, int(sys.argv[1]) if len(sys.argv) > 1 else 3, 20261031

key = json.loads((ROOT / os.environ.get("KEY", "runner/answer_key.json")).read_text())
pairs = [(q, rep) for q in key for rep in range(1, REPEATS + 1)]
rng = random.Random(SEED)
rng.shuffle(pairs)
schedule = [(i, q, rep, rng.sample(["FLASH", "STANDARD"], 2)) for i, (q, rep) in enumerate(pairs)]

done = set()
if OUT.exists():
    for line in OUT.read_text().splitlines():
        r = json.loads(line)
        done.add((r["qid"], r["repeat"], r["mode"]))
lock = threading.Lock()

def run_pair(item):
    i, q, rep, modes = item
    for pos, mode in enumerate(modes):
        if (q["qid"], rep, mode) in done:
            continue
        space = SPACES.get(q.get("agent")) or SPACE_ID
        r = ask(q["question"], mode, space_id=space)
        r.update(qid=q["qid"], repeat=rep, pair_index=i, position_in_pair=pos, space_id=space)
        with lock:
            with OUT.open("a") as f:
                f.write(json.dumps(r) + "\n")
            print(f"{time.strftime('%H:%M:%S')} pair {i:3d} {mode:8s} {q['qid']:30s} r{rep} {r['status']} {r['elapsed_s']:.1f}s sql={len(r['sql'])}", flush=True)

with ThreadPoolExecutor(WORKERS) as ex:
    list(ex.map(run_pair, schedule))
print("done")
