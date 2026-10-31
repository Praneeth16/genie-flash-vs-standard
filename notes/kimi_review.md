# Independent review: article/draft.md

Reviewed against the round 1 files (results/raw.jsonl, results/grades.jsonl, results/summary.json, runner/answer_key.json, notes/adjudications.json) and round 2 files (results/raw_r2.jsonl, results/grades_r2.jsonl, results/summary_r2.json, runner/answer_key_r2.json, notes/adjudications_r2.json). All counts were recomputed from the JSONL files with Python; the three round 1 adjudications and the two round 2 adjudications in notes/ were applied where the article's numbers depend on them.

## What checks out (factual accuracy, point 1)

Every load-bearing number and quote in the article was verified against the raw data:

- Line 13 quote: Flash repeat 1 of partial-reversal-open says verbatim "decreased by 300 shipments, from 900 in September 2026 to 600 in October 2026" (bold markers stripped). Flash elapsed times on that question: 9.7 to 11.0 s, median 10.1 s, so "about 10 seconds" is accurate.
- Line 15: Standard times on the same question run 13.05 to 32.05 s, so "13 to 32 seconds" is exact. "Stops on 15 October", "30 shipments a day", "40" all match answer_key_r2.json facts.
- Line 17: all five Flash runs and all five Standard runs split exactly as described. The quote "October is essentially a complete month" appears verbatim in Flash repeat 5.
- Line 45: 280 + 200 = 480 requests. Judge blinding confirmed in runner/judge.py ("They never carry the mode, timing or repeat number").
- Line 49: round 1 directed conclusions are 40/40 for both modes; round 2 directed conclusions are Flash 38/40 (37 in raw grades plus the duplicate-reversal-directed adjudication) and Standard 40/40. Round 1 lookup pass: Flash 40/40.
- Line 53 figure caption: Lookup Flash 40/40, Standard 39/40 (38 raw plus the complaints-reversal-lookup adjudication); Directed Flash 36/40, Standard 40/40; Open Flash 26/40, Standard 37/40 (36 raw plus the contribution-control-open adjudication). All match.
- Line 59: round 2 open reversal traps (partial, duplicate, zonemix) conclusion counts: Flash 0/15, Standard 10/15 (5 + 2 + 3). Exact.
- Line 61: all five duplicate-reversal-open Flash responses say "doubled"; all five zonemix-reversal-open Flash responses conclude the rate got worse. Flash ran exactly one SQL query in 35 of 40 round 2 open responses ("usually ran one query" holds); Standard ran 2 to 7.
- Line 63: all five Standard partial-reversal-open responses state the October data stops on 15 October. Round 1 delivery-reversal-open: Standard met the "both zones got slower" criterion in 4 of 5 runs. The 6.8 to 4.2 day averages and the 20% to 80% local share with each zone one day slower match notes/ground_truth_output.txt and the answer key (also validates the animation caption on line 7).
- Line 65 figure caption: partial-reversal 0/5 vs 5/5; duplicate-reversal 0/5 vs 2/5; zonemix-reversal 0/5 vs 3/5; zonemix-control 0/5 vs 0/5; the other three open questions 5/5 vs 5/5. All confirmed from grades_r2.jsonl criterion 4.
- Line 67: round 2 open median times recomputed from raw_r2.jsonl: Flash 11.2 s, Standard 26.3 s.
- Line 71: 10/15 and duplicate 2/5 confirmed.
- Line 73: "Delivery time improved by 2.6 days month-over-month" appears verbatim in delivery-reversal-lookup Standard repeat 1. On zonemix-control-open, Standard repeats 1 and 5 each ran a two-proportion z-test (z = 1.4) and declined to call the rate worse; exactly twice.
- Line 75: recomputed round 1 open word medians: Standard 232.5, Flash 62.5. Unsupported-claim totals across round 1: Standard 61 (62 raw minus the adjudicated lookup), Flash 30.
- Line 90: Standard led in both rounds (121 vs 105 and 68 vs 43 on pass). Both runs executed on 2026-10-31 per the run timestamp files.
- Line 92: repository link matches the public repo.

No fabricated, transposed, or overstated numbers were found. The findings below are therefore dominated by terminology, scope, and readability issues, not factual errors.

## Findings, most severe first

### 1. "Trap" is used 10 times, violating the project's own terminology rule (style rule 3)

- Lines 31, 37, 59, 65, 71, 73, 90. E.g., line 31: "I made up a delivery company called Meridian Parcel and hid traps in its data. Each trap is a number that points the wrong way at first glance..." and line 59: "...Flash reached the right conclusion on the partial month, duplicate and mix traps in 0 of 15 runs."
- What is wrong: notes/style_rules.md rule 3 says the prose terms are "reversal network and control network. Never 'trap', 'variant', 'version' in prose." The draft uses "trap" 10 times, including in the method section that should define the terminology, and line 37 then defines "control network" against an undefined "trap" counterpart, so the rule-compliant term "reversal network" never appears at all. A reader (or a later editor applying the style sheet) gets two vocabularies.
- Fix: rewrite the method paragraph to introduce the paired terms once, e.g. "Each reversal network hides a number that points the wrong way at first glance, plus one check that shows the truth. Each control network looks the same, but the first number is correct." Then replace the remaining uses: line 59 "the partial, duplicate and mix reversal networks", line 71 "those 15 reversal runs", line 65 caption "the control for the zone mix case", line 73 "the misreading the reversal network was built to catch", line 90 "each reversal network has one designed check".

### 2. The two rounds are never defined, but the headline result depends on the difference (readability)

- Line 45: "Over two rounds, I sent 480 requests, each in a fresh conversation."
- What is wrong: the article later cites "the first round" (lines 49, 53, 63, 75) and "the second round" (lines 49, 59, 65, 67) as if the reader knows what distinguishes them. The rounds test different traps (round 1: delivery mix, complaints, contribution, refunds, missing data; round 2: partial month, duplicate rows, test parcels, zone mix) and different question mixes (round 2 has no lookups). The single most quoted result, "0 of 15 runs" on line 59, is round 2 only, and the animation at the top is a round 1 trap. A general reader cannot tell whether the rounds are replicates, a pilot and a rerun, or different tests, so they cannot judge how much weight to put on each number.
- Fix: add one or two sentences to "How I tested it" stating that round 1 used four everyday cases plus missing-data questions, and round 2 added four new traps (partial month, duplicate load, internal test parcels, zone mix) with harder open questions. Name which round each later number comes from at first use.

### 3. The text and the figure beside it use two different score bars without saying so (readability, lines 49 vs 53)

- Line 49: "Both reached the right conclusion in all 40 directed responses in the first round." Line 53 figure caption: "Directed: Flash 36/40, Standard 40/40."
- What is wrong: the text counts correct conclusions; the figure counts answers that "met every check" (all four criteria). A reader sees "all 40" and "36/40" for the same category three paragraphs apart and no explicit statement that two measures exist. Line 55 explains the gap ("the right answer without the numbers behind it") but only after the figure, and never names the distinction.
- Fix: introduce the two measures once in the method section (pass = met every check; correct conclusion = the final claim was right), then have line 49 read "...both reached the right conclusion in all 40; on the stricter every-check bar, Flash met 36 and Standard 40 (figure)."

### 4. The unsupported-claim counts are scoped to all answers, but the sentence scopes itself to open answers (accuracy-adjacent, line 75)

- Line 75: "Its median open answer in the first round had 233 words, against 63 for Flash, and the judge found 61 unsupported claims in Standard's answers against 30 in Flash's."
- What is wrong: the 61 and 30 are totals across all 280 first round answers; within open answers only, the judge found 25 (Standard) and 8 (Flash). The sentence's first clause is explicitly about open answers, so a reader reasonably reads the second clause the same way. Separately, the recomputed medians are 232.5 and 62.5 words, so "233" and "63" both round up; "about 230" and "about 63" or "233" with the .5 acknowledged would be cleaner.
- Fix: "Its median open answer in the first round had about 233 words, against 63 for Flash. Across all first round answers, the judge found 61 unsupported claims in Standard's against 30 in Flash's."

### 5. Headings do not follow style rule 1 (subject + present-tense verb)

- Lines 9, 19, 29, 47, 57, 69, 77, 88: "One question, two answers", "Fast and slow thinking", "How I tested it", "When fast is enough", "When the obvious number is wrong", "So which one should you use?", "What this test can't tell you".
- What is wrong: rule 1 requires each heading to start with its subject and a present-tense verb (example given: "Flash misses the mix shift on open questions"). Most headings here are noun phrases, questions, or start with When/So/What/How. The recommendation list items (lines 81 to 82) also start with "If" rather than a subject.
- Fix: either rewrite the headings to the prescribed pattern (e.g. "Flash ties Standard on directed questions", "Flash misses the traps on open questions", "Standard overthinks some answers", "The question tells you which mode to use") or amend style_rules.md to record the question-style headings as a deliberate choice. Given the article's Kahneman hook, some headings may justify an exception, but that exception should be in the rules file, not silent.

### 6. Results sections do not use the directional verbs required by style rule 5

- Lines 49, 59, 71: "did as well as Standard", "reached the right conclusion", "got 38 of 40", "got 10 of those 15 trap runs right".
- What is wrong: rule 5 says results use verbs that show direction: "catches", "misses", "ties", "takes longer". The draft's result sentences use neutral report verbs throughout. Minor, because the numbers carry the direction anyway, but it is a written rule.
- Fix: small rewrites where natural: "Flash ties Standard on directed questions", "Flash misses all 15 trap conclusions; Standard catches 10", "Standard catches the duplicate rows in only two of five runs."

### 7. "Disclosure:" uses a label colon, against the letter of style rule 6

- Line 100: "*Disclosure: I work at Databricks. ..."
- What is wrong: rule 6 allows colons only before lists. All body colons (lines 31, 39, 79) correctly introduce lists; this one does not. The figure captions (lines 53, 65) use the same label-colon pattern, which is arguably fine as table-cell-style labels under rule 2, but line 100 is plain prose.
- Fix: "*Disclosure. I work at Databricks. ...*" or fold into a sentence: "*I work at Databricks. Opinions here are my own. ...*"

### 8. "Wait" as a near-measure brushes against style rule 3

- Line 3: "I tested when the slow answer is worth the wait." Line 84: "wait for Standard to look."
- What is wrong: rule 3 bans "wait" as a measure of completion time. Both uses are colloquial rather than measurements, and the article measures time in seconds everywhere else, so this is a borderline case. Flagging only because the subtitle is the most-read line of the article.
- Fix: optional. "I tested when the slow answer earns its extra seconds" keeps the hook and the rule.

### 9. Genie itself is never glossed for the general reader (readability)

- Line 11: "I asked Genie how shipment volume in one delivery network changed from September to October."
- What is wrong: the article is framed for a general Medium reader, but the first mention of Genie assumes the reader knows it is Databricks' natural-language data assistant. The product framing arrives only at line 23, and even there it describes the modes, not the product.
- Fix: add half a sentence at first use, e.g. "I asked Genie, Databricks' assistant that answers data questions in plain language, how shipment volume..."

## Point 2: Kahneman accuracy

The claims in lines 21 and 84 are accurate and fairly stated:

- System 1 as fast and automatic, System 2 as slow and effortful matches the book's core definitions.
- "What you see is all there is" is Kahneman's own term (WYSIATI), and the gloss "builds the best story it can from the information it has, and it does not ask what is missing" is a faithful paraphrase of his description of System 1's coherence-seeking and insensitivity to absent evidence.
- "System 2 ... checks whether the first answer holds up" is a simplification: Kahneman also stresses that System 2 is lazy and often endorses System 1 uncritically. For this article the simplification is harmless, because the results section ("Slow is not always right", Standard overthinking and declining correct conclusions) demonstrates exactly that caveat in the Genie setting.
- The article does not mention that Kahneman presents the two systems as useful fictions rather than literal brain modules. Given "Genie Agent mode now has a version of both" is explicitly an analogy, this omission is acceptable for Medium.
- Bibliographic details (Farrar, Straus and Giroux, 2011) are correct.

## Point 3: story and readability summary

The arc is strong: a concrete hook with two conflicting answers and verbatim quotes, a short Kahneman frame, a compact method section, findings ordered from reassuring to alarming, honest "Slow is not always right" counterweight, actionable guidance, and a candid limitations paragraph. The guidance on lines 81 to 82 is fully supported by the findings (directed questions: both modes tie; unknown risks: Flash failed every open trap run). The untested suggestion about agent instructions is correctly hedged. The main readability debts are findings 2, 3, and 9 above: undefined rounds, two unlabeled score bars, and no product gloss. Nothing is padded; at roughly 1,100 words the length is right for Medium.

## Verdict

Not ready to publish as is, but close. The factual spine is clean: every number, range, median, quote, and "in all five runs" claim I could test reproduces exactly from the raw data and the documented adjudications. What blocks publication is compliance with the article's own style sheet and two clarity gaps around the test design.

Top 3 changes:

1. Purge "trap" from the prose and introduce "reversal network / control network" in the method section (finding 1; ten occurrences).
2. Define round 1 versus round 2 in "How I tested it" and label the two score bars (pass vs correct conclusion) before they are used (findings 2 and 3).
3. Fix the scope of the unsupported-claim sentence on line 75 so the 61 vs 30 totals are clearly across all first round answers (finding 4).
