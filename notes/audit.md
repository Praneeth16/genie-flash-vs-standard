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

## Round 2 audit (2026-10-31)

Read in full: partial-reversal-open r1 Flash, testparcels-reversal-open r1 Flash, testparcels-reversal-directed r1 Standard, zonemix-control-open r1 Standard, duplicate-reversal-open r1 Flash, duplicate-reversal-directed r2 Standard, and the opening of every zone-mix open response (20). No verdict overturned.

- Test parcel criteria 1 and 3 require stating the number of test parcels and their effect on the all-rows average. Responses that only filtered `is_test` fail them even with the right conclusion. That is why the article leads round 2 with the correct-conclusion rate.
- duplicate-reversal-directed criterion 2 requires naming the two loads. Standard r2 found the duplicates but called the cause a "data-loading artifact" and failed it.
- zonemix-control-open: Flash said "worse" in all 5 runs but never split by zone, so it fails criterion 4 ("worse in both zones"). Standard r1 and r5 ran a significance test and declined to call it worse.
