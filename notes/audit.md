# Manual audit of the LLM judge (2026-10-31)

Sample read in full (judge reasons plus response text), 55 responses, dumped in `audit_dump.txt`:
- every response to the open delivery questions (NW-4127, NW-2863) and the open NW-6208 contribution question, both modes
- every response to the directed NW-3916 contribution question and missing-routing, both modes
- every Standard lookup failure, and every other failure in refunds-control-directed and contribution-reversal-directed

Result: no verdict overturned. The judge applied the criteria as written. The main source of Flash failures on directed/contribution questions is omission of supporting figures (e.g., net contribution stated without revenue, cost or credits), which the pre-written criteria require. That is why the article reports the correct-conclusion rate separately.

Notable cases found in the audit:
- contribution-reversal-open r3 STANDARD: joined invoices to credit rows, reported October revenue $160,000 and net $33,000 (the join trap).
- contribution-reversal-open r3 FLASH: grouped by day then took MAX per month, reported $3,000 and $3,500, concluded "Yes".
- missing-routing: Standard opened with "Yes" and a 1-day saving in all 5 runs. Flash ran a difference-in-differences against the pooled other networks (0.16 days), which includes NW-4127's mix-driven drop.
- delivery-reversal-lookup r1 STANDARD: added "Delivery time improved by 2.6 days" to a lookup answer.
- missing-paid: by exact phrase, 4 Standard responses (r1, r2, r3, r5) and 2 Flash responses (r1, r2) stated the $60 as paid out.

This audit was done on the first full grading pass (results/grades_v1.jsonl). The final pass (results/grades.jsonl) agrees with it on 276 of 280 pass/fail verdicts.
