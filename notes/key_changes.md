2026-10-31: contribution-reversal conclusion criterion relaxed after pilot grading of 8 responses (it required a gross-margin statement the question did not ask for). All responses regraded with the final key.

2026-10-31, after an independent Codex review (notes/codex_review.md):
- refunds-control criterion 1 and facts: said v2 covers every NW-8045 shipment. Wrong: 21 on-time NW-8045 shipments were promised before 15 October. Corrected to "every late shipment". Eligibility (6 shipments, $120) is unchanged.
- missing-paid criterion 4: clarified that stating payment records are missing counts as naming the needed evidence.
- judge packets now include the full table list with column comments, so true statements about absent columns (e.g., no customer ID) are not counted as unsupported.
- All 280 responses regraded. First full pass kept as results/grades_v1.jsonl and results/summary_v1.json. The two passes agree on 276 of 280 pass/fail verdicts (1106 of 1120 criteria). One flip is the refunds-control fix, three are borderline responses.

2026-10-31, after a second Codex check (notes/codex_review_2.md): three Standard verdicts in the final pass applied the criteria unevenly (contribution-control-open r2, missing-paid r4, complaints-reversal-lookup r4). Settled by hand with one rule (the final conclusion counts, and a true remark is not an unsupported claim). All three became passes. Recorded in notes/adjudications.json and applied by runner/analyze.py. results/grades.jsonl keeps the raw judge output.

2026-10-31, round 2, after a Codex check (notes/codex_review_3.md): two Flash verdicts applied the duplicate criteria unevenly (duplicate-control-open r3 criterion 3, duplicate-reversal-directed r5 criterion 4). Settled to match the other repeats of the same question. Recorded in notes/adjudications_r2.json. Neither changes a pass; Flash's directed correct-conclusion count moves from 37 to 38 of 40. The round 2 answer key itself was not changed after the run.
