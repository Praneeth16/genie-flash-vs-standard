## Wrong or unsupported claims

- [article/draft.md:21](article/draft.md#L21): “Missed the zone check … in all five runs” overstates the result. Flash repeat 5 queried averages and counts by zone and explicitly mentioned the mix shift (`results/raw.jsonl:194`). **One of five investigated zones; zero met the complete reporting rubric.** Use that distinction.

- [article/draft.md:19](article/draft.md#L19), also lines 96, 98 and 104: “40 questions” conflates questions with repeats. Each level contains **eight distinct questions and 40 responses per mode**. Replace “questions” with “responses” where reporting these denominators.

- [article/draft.md:77](article/draft.md#L77), also line 140: “280 requests … no request failed” excludes the interrupted attempts. The documented three replacements imply **283 client attempts yielding 280 retained responses**. Report successful benchmark slots separately from attempts and client failures.

- [article/draft.md:60](article/draft.md#L60): “The data ends in October” is too broad. Python reconstruction and `notes/ground_truth_output.txt:45` show latest **ship_date October 28; delivered_date November 3**. Specify that shipment dates end in October.

- [article/draft.md:150](article/draft.md#L150): Open questions were not the hardest by observed pass rate. Missing-evidence responses passed **15% Flash / 25% Standard**, versus **65% / 92.5%** for open responses. Qualify “hardest” to exclude missing-evidence questions or remove it.

- [article/draft.md:155](article/draft.md#L155): “Because the instructions defined them” asserts an untested cause. Both modes received those instructions; no run removed them. Say the checks were supplied in the instructions and their contribution was not isolated.

## Methodology or code issues

- [runner/answer_key.json:340](runner/answer_key.json#L340), also line 355: The refund-control criterion incorrectly requires v2 for every shipment. Reconstructing `sql/01_build_data.sql:73` gives **21 NW-8045 shipments under v1 and 27 under v2**; only the eight late shipments all use v2. `results/grades.jsonl:176` consequently rejects Standard directed repeat 4’s correct explanation. Correct the key and regrade; eligibility remains **six shipments, $120**.

- [runner/judge.py:33](runner/judge.py#L33): Judge packets omit table schemas. Consequently, `results/grades.jsonl:12`, `:132` and `:250` count truthful statements about missing customer identifiers as unsupported because the response did not query every schema. The DDL confirms those statements. Supply schema evidence and reassess the unsupported-claim totals.

- [results/grades.jsonl:146](results/grades.jsonl#L146): Missing-paid criterion 4 uses inconsistent standards. Flash repeat 3 passes despite the reason admitting it does not state what evidence is needed; Standard repeat 3 fails at line 142 despite identifying absent payout records and a payment ledger. Define whether naming missing records implicitly satisfies the criterion, then adjudicate consistently.

- [notes/audit.md:15](notes/audit.md#L15): The audit reports three payout assertions per mode. Raw responses show **four Standard openings and two Flash openings** asserting payment, matching article line 134. Correct the audit note.

## Hygiene

none

