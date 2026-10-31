**Wrong or unsupported claims**

- [article/draft.md:56](article/draft.md:56), :86 — Calling the instructions hypothesis “wrong” overstates the ablation. Removing text definitions left refund rules in schema comments ([sql/01_build_data.sql:163](sql/01_build_data.sql:163)). The results show those text definitions were unnecessary for similar performance. **Fix:** state that narrower finding and acknowledge the remaining metadata guidance.

**Grading inconsistencies**

- [results/grades_r2.jsonl:98](results/grades_r2.jsonl:98) — `duplicate-control-open`, Flash repeat 3 fails criterion 3 because 2,000 is a raw count. Repeats 1, 2, 4 and 5 pass that criterion at lines 51, 82, 125 and 14 despite also using `COUNT(*)` without establishing uniqueness. **Fix:** apply one distinct-count standard across all five responses.

- [results/grades_r2.jsonl:13](results/grades_r2.jsonl:13), :80 — `duplicate-reversal-directed`, Flash repeat 5 fails criterion 4 while repeat 4 passes. Both show flat volume of 1,000 distinct shipments, 2,000 October rows and 1,000 duplicated IDs; neither establishes the two loads. Repeat 5 presents this through a table. **Fix:** apply the same standard for table evidence and load attribution, then regenerate affected counts.

**Design or code issues**

- [runner/run_benchmark.py:34](runner/run_benchmark.py:34) — Missing per-agent settings silently fall back to `GENIE_SPACE_ID`. Python reproduced an `r2` question selecting the generic round 1 agent. **Fix:** require an explicit mapping for every named agent. Saved round 2 routing was correct.

- [runner/analyze.py:15](runner/analyze.py:15) — Selecting round 2 through `KEY/RAW/GRADES/SUMMARY` still loads round 1 adjudications by default. Python reproduced `KeyError ('contribution-control-open', 2, 'STANDARD')`. **Fix:** scope adjudications to the selected round or require `ADJ` explicitly. The documented override avoids this.

- [notes/ground_truth_round2_output.txt:35](notes/ground_truth_round2_output.txt:35) — The final saved check differs from [sql/04_ground_truth_round2.sql:39](sql/04_ground_truth_round2.sql:39). It reports 25,096 versus 9,096 using the older filter; the current original-network filter should yield 9,096 versus 9,096. **Fix:** recapture the current reference output.

Python reproduced both summaries exactly. All eight new networks matched the stated design and key arithmetic; Figure 5 matched criterion-4 counts. Commit `584272a` precedes the recorded run start. No files were modified.

