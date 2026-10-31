"""One Agent mode request over SSE. Returns a dict with the answer, SQL calls, timing and raw events."""
import json, os, time
import requests
from databricks.sdk import WorkspaceClient

PROFILE = os.environ.get("DATABRICKS_CONFIG_PROFILE")
SPACE_ID = os.environ["GENIE_SPACE_ID"]

_w = WorkspaceClient(profile=PROFILE)

def ask(question, mode, timeout=300):
    url = f"{_w.config.host}/api/2.0/genie/agents/{SPACE_ID}/responses"
    body = {"input": [{"type": "message", "role": "user", "content": [{"type": "input_text", "text": question}]}],
            "execution_mode": mode, "enable_viz": False}
    headers = {**_w.config.authenticate(), "Accept": "text/event-stream", "Content-Type": "application/json"}
    out = {"mode": mode, "question": question, "events": [], "status": None, "error": None,
           "conversation_id": None, "response_id": None, "answer": "", "sql": [], "reasoning_items": 0}
    t0 = time.time()
    out["started_at"] = t0
    first_event = None
    try:
        with requests.post(url, json=body, headers=headers, stream=True, timeout=(30, timeout)) as r:
            if r.status_code != 200:
                out["status"], out["error"] = "http_error", f"{r.status_code} {r.text[:2000]}"
                out["elapsed_s"] = time.time() - t0
                return out
            for line in r.iter_lines(decode_unicode=True):
                if not line or not line.startswith("data:"):
                    continue
                ev = json.loads(line[5:].strip())
                if first_event is None:
                    first_event = time.time() - t0
                out["events"].append({"t": round(time.time() - t0, 3), **ev})
                kind = ev.get("type")
                if kind == "response.created":
                    resp = ev.get("response", {})
                    out["conversation_id"], out["response_id"] = resp.get("conversation_id"), resp.get("id")
                elif kind in ("response.completed", "response.failed"):
                    resp = ev.get("response", {})
                    out["status"] = resp.get("status")
                    out["error"] = resp.get("error")
                    out["conversation_id"] = out["conversation_id"] or resp.get("conversation_id")
                    for item in resp.get("output", []):
                        if item.get("type") == "message":
                            out["answer"] += "".join(c.get("text", "") for c in item.get("content", []))
                        elif item.get("type") == "function_call":
                            try:
                                args = json.loads(item.get("arguments") or "{}")
                            except json.JSONDecodeError:
                                args = {"raw": item.get("arguments")}
                            out["sql"].append({"name": item.get("name"), "args": args})
                        elif item.get("type") == "reasoning":
                            out["reasoning_items"] += 1
                    break
    except Exception as e:  # network errors stay in the record, never retried
        out["status"], out["error"] = "client_error", repr(e)
    out["elapsed_s"] = round(time.time() - t0, 3)
    out["first_event_s"] = first_event
    return out

if __name__ == "__main__":
    import sys
    r = ask(sys.argv[2], sys.argv[1])
    print(json.dumps({k: v for k, v in r.items() if k != "events"}, indent=1)[:6000])
    print("event types:", sorted({e.get("type") for e in r["events"]}))
