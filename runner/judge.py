"""Blind grading. Packets carry question, response, SQL evidence, answer-key facts and criteria.
They never carry the mode, timing or repeat number. Writes results/grades.jsonl."""
import json, os, re, sys, threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from databricks.sdk import WorkspaceClient

ROOT = Path(__file__).resolve().parent.parent
RAW, OUT = ROOT / "results/raw.jsonl", ROOT / "results/grades.jsonl"
JUDGE = "databricks-claude-opus-5-5"
w = WorkspaceClient(profile=os.environ.get("DATABRICKS_CONFIG_PROFILE"))
key = {q["qid"]: q for q in json.loads((ROOT / "runner/answer_key.json").read_text())}

SYSTEM = """You grade one analytics answer against an answer key. You do not know which system wrote it.
Grade each criterion as pass or fail. A criterion passes only when the response itself states or clearly shows it.
Equivalent numbers pass (4.2 = 4.20 days, 3% = 0.03, $20K = $20,000). Equivalent queries and explanations get the same credit.
Grade the final conclusion the response gives, not intermediate tables it later corrects.
Count unsupported claims: statements that the data and the response's own queries do not support (invented causes, wrong numbers presented as fact, causal claims, invented data).
Return only JSON: {"criteria": [{"pass": true|false, "reason": "..."}, x4], "unsupported_claims": <int>, "unsupported_examples": ["..."], "acknowledges_missing_evidence": true|false|null}
Set acknowledges_missing_evidence to null unless the question asks for data the tables do not contain."""

def table_schemas():
    sql = (ROOT / "sql/01_build_data.sql").read_text()
    out = []
    for name, body in re.findall(r"CREATE OR REPLACE TABLE (\w+) \((.*?)\) COMMENT", sql, re.S):
        if not name.startswith("_"):
            cols = [l.strip().rstrip(",") for l in body.strip().splitlines()]
            out.append(f"{name}: " + "; ".join(cols))
    return "\n".join(out)

SCHEMAS = table_schemas()

def fix_text(t):
    try:
        return t.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return t

def packet(r):
    q = key[r["qid"]]
    sql = "\n\n".join(f"-- {s['args'].get('title', '')}\n{s['args'].get('sql', s['args'])}" for s in r["sql"]) or "(no SQL calls)"
    crit = "\n".join(f"{i+1}. {c}" for i, c in enumerate(q["criteria"]))
    answer = re.sub(r"\\\[\[\d+\]\(https?://[^)]*\)\\\]", "", fix_text(r["answer"] or "(no answer)"))
    return f"QUESTION\n{q['question']}\n\nTABLES THE SYSTEM COULD QUERY (complete list, with column comments)\n{SCHEMAS}\n\nANSWER KEY FACTS\n{q['facts']}\n\nCRITERIA\n{crit}\n\nRESPONSE\n{answer}\n\nSQL THE SYSTEM RAN\n{sql}"

def grade(r):
    if r["status"] != "completed" or not r["answer"]:
        return {"criteria": [{"pass": False, "reason": "technical failure"}] * 4, "unsupported_claims": 0,
                "unsupported_examples": [], "acknowledges_missing_evidence": None, "technical_failure": True}
    for attempt in range(3):
        resp = w.api_client.do("POST", f"/serving-endpoints/{JUDGE}/invocations", body={
            "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": packet(r)}],
            "max_tokens": 4000})
        text = resp["choices"][0]["message"]["content"]
        if isinstance(text, list):
            text = "".join(p.get("text", "") for p in text if isinstance(p, dict))
        m = re.search(r"\{.*\}", text, re.S)
        try:
            g = json.loads(m.group(0))
            assert len(g["criteria"]) == 4
            g["technical_failure"] = False
            return g
        except Exception:
            continue
    raise RuntimeError(f"judge output unparsable for {r['qid']}")

if __name__ == "__main__":
    rows = []
    for l in RAW.read_text().splitlines():
        try:
            rows.append(json.loads(l))
        except json.JSONDecodeError:
            pass
    done = set()
    if OUT.exists():
        done = {(g["qid"], g["repeat"], g["mode"]) for g in map(json.loads, OUT.read_text().splitlines())}
    todo = [r for r in rows if (r["qid"], r["repeat"], r["mode"]) not in done]
    lock = threading.Lock()
    def work(r):
        g = grade(r)
        g.update(qid=r["qid"], repeat=r["repeat"], mode=r["mode"], passed=all(c["pass"] for c in g["criteria"]))
        with lock, OUT.open("a") as f:
            f.write(json.dumps(g) + "\n")
    with ThreadPoolExecutor(int(sys.argv[1]) if len(sys.argv) > 1 else 6) as ex:
        list(ex.map(work, todo))
    print("graded", len(todo))
