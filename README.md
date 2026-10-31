# Thinking, Fast and Slow with Databricks Genie

Companion repo for the article that compares Genie Agent mode **Flash** with **standard Agent mode** (called Standard here). Both modes answered the same 28 questions five times each on a synthetic parcel company, Meridian Parcel. That makes 280 requests in 140 randomized pairs. A blind LLM judge graded every response against four criteria per question.

All data is synthetic. Results are from one run on 31 October 2026.

## Results at a glance

| Question level | Flash pass | Standard pass | Median completion time (Flash / Standard) |
|---|---|---|---|
| Lookup | 40/40 | 39/40 | 8.6s / 9.1s |
| Directed (names the check) | 36/40 (conclusion 40/40) | 40/40 (conclusion 40/40) | 12.0s / 13.1s |
| Open (does not name the check) | 26/40 | 37/40 | 12.4s / 16.5s |
| Missing evidence | 3/20 | 5/20 | 11.9s / 14.4s |

The gap on open questions comes from the delivery case. There, the overall average falls only because the zone mix shifts. On NW-4127, Standard reported that both zones got slower in 4 of 5 runs. Flash never did. In one run Flash split the on-time rate by zone and mentioned the mix, but it still said delivery got faster. Full numbers are in `results/summary.json`.

![Pass rate by question level](figures/fig2-pass-by-level.png)

## Layout

- `article/draft.md` is the article. `medium/` holds the Medium build script, publish notes and the hero image prompt.
- `sql/01_build_data.sql` builds the seven tables. `sql/02_ground_truth.sql` is the reference SQL. `notes/ground_truth_output.txt` holds its output.
- `runner/answer_key.py` defines the 28 questions, four criteria each, and the answer-key facts. It writes `answer_key.json`. The Genie agent never sees this file.
- `runner/create_agent.py` creates the Genie agent: tables, text instructions and join specs.
- `runner/genie_call.py` makes one Agent mode request over SSE with `execution_mode` set to `FLASH` or `STANDARD`.
- `runner/run_benchmark.py [workers]` runs the 280 requests. It uses seed 20261031, can resume and never retries.
- `runner/judge.py` grades blind packets. They hold no mode, timing or repeat number.
- `runner/analyze.py` writes `results/summary.json`.
- `results/raw.jsonl` holds every response with its SQL and timing. Workspace hostnames are replaced with `<workspace-host>`. `results/grades.jsonl` holds every verdict.
- `notes/` holds the judge audit, the run incident log and the answer-key change log.
- `figures/` and `screenshots/` hold the images used in the article. `figures/make_*.py` regenerate the charts.

## Run it on your own workspace

You need a Databricks workspace with Genie Agent mode, the Flash preview enabled by an admin, a SQL warehouse, and a Claude (or other chat) serving endpoint for the judge.

```bash
uv venv .venv && uv pip install --python .venv/bin/python databricks-sdk requests matplotlib numpy pillow

export DATABRICKS_CONFIG_PROFILE=<your-profile>
export MERIDIAN_CATALOG=<catalog-you-can-write-to>
export WAREHOUSE_ID=<sql-warehouse-id>

.venv/bin/python sql/run_sql.py sql/01_build_data.sql
.venv/bin/python sql/run_sql.py sql/02_ground_truth.sql      # check the expected values
.venv/bin/python runner/answer_key.py
export GENIE_SPACE_ID=$(.venv/bin/python runner/create_agent.py | head -1)

cd runner
../.venv/bin/python run_benchmark.py 3
../.venv/bin/python judge.py 6        # judge endpoint: JUDGE in judge.py
../.venv/bin/python analyze.py
```

The tables are written to `$MERIDIAN_CATALOG.meridian_parcel`. Change `JUDGE` in `runner/judge.py` if your workspace uses a different endpoint name.

## Limits

- The data is small and synthetic. Each case has one designed check.
- There are eight open questions. Five repeats measure stability, not new problems. The 95% bootstrap interval on the open-question difference is 7.5 to 52.5 percentage points.
- One LLM judge graded all 280 responses. Two full grading passes agree on 276 of 280 verdicts, and three inconsistent verdicts were settled by hand (`notes/adjudications.json`, applied in `runner/analyze.py`). 55 were read by hand and no verdict was overturned (`notes/audit.md`). Answer-key changes are logged in `notes/key_changes.md`, and the Codex review that prompted the last one is in `notes/codex_review.md`.
- Completion time was measured on the client. Cost and token use were not measured.
- Flash is in Beta. Results describe one run on one day.

Disclosure: the author works at Databricks. Opinions are the author's own.
