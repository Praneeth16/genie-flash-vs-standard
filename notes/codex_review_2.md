## Status of earlier issues

- **Fixed:** question/response denominators; 283 attempts versus 280 retained responses; shipment-date cutoff; “hardest” characterization; untested causal attribution to instructions.
- **Fixed:** refund-control answer key; schema evidence in judge packets; missing-paid criterion 4 consistency; audit payout counts.
- **Partly fixed:** zone-check overstatement. The article now distinguishes investigation from rubric success, but README retains the overstatement.

## Remaining mismatches

- [README.md:16](/Users/praneeth.paikray/Documents/Code/04-content/articles/genie-flash-vs-standard/README.md:16): “Flash found the mix shift … in 0 of 5 runs” remains inaccurate. Repeat 5 investigated zones and explicitly mentioned the mix shift ([raw.jsonl:194](/Users/praneeth.paikray/Documents/Code/04-content/articles/genie-flash-vs-standard/results/raw.jsonl:194)). Say **one investigated and mentioned it; zero satisfied the complete rubric**.

`python3` reproduced the entire summary exactly. All other numerical claims match the recorded results, allowing displayed rounding. This includes figure alt text, actual Figure 2/3 labels, timing, unsupported-claim totals, 276/280 verdict agreement, and 1106/1120 criterion agreement.

## New problems

The regrade introduced three inconsistent judgments:

- [grades.jsonl:94](/Users/praneeth.paikray/Documents/Code/04-content/articles/genie-flash-vs-standard/results/grades.jsonl:94): Standard contribution-control-open repeat 2 newly fails despite stating contribution rose $30,000→$35,000 and “In dollars, October was better.” Its accurate margin distinction does not negate the required conclusion.
- [grades.jsonl:57](/Users/praneeth.paikray/Documents/Code/04-content/articles/genie-flash-vs-standard/results/grades.jsonl:57): Standard missing-paid repeat 4 newly fails for its opening wording despite explicitly concluding “not a recorded payout.” Equivalent Flash openings with closing disclaimers pass at lines 143 and 230, contrary to consistent application of the final-conclusion instruction.
- [grades.jsonl:227](/Users/praneeth.paikray/Documents/Code/04-content/articles/genie-flash-vs-standard/results/grades.jsonl:227): Standard complaints-reversal-lookup repeat 1 now passes its unsupported “full month” assertion, while repeat 4 fails essentially the same assertion at line 76.

Adjudicate these consistently, then regenerate affected aggregates and prose. The current numbers accurately reproduce the saved judgments; those judgments still need correction.