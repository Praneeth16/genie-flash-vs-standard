# Thinking, Fast and Slow with Databricks Genie

*Genie can now answer fast or slow. I tested when the slow answer is worth the wait.*

Praneeth Paikray, 31 October 2026

## One question, two answers

Databricks Genie answers questions about company data. You ask in plain English, and it writes and runs the database queries for you. I asked it how shipment volume in one delivery network changed from September to October.

With Flash switched on, Genie answered in about 10 seconds. It said volume "decreased by 300 shipments, from 900 in September 2026 to 600 in October 2026."

With Flash switched off, Genie took 13 to 32 seconds and reached the opposite conclusion. The network's October data stops on 15 October, so the two months cover different numbers of days. Per day, volume went up, from 30 shipments in September to 40 in October.

Both answers came from the same agent reading the same data. The only difference was one button. I asked the question five times in each mode, and the answers split the same way every time. In one run, Flash even wrote that "October is essentially a complete month". It never checked.

## Fast and slow thinking

In *Thinking, Fast and Slow*, Daniel Kahneman describes two ways people think. System 1 is fast and automatic, and it answers from whatever is in front of it. System 2 is slow and takes effort, and it can check whether the first answer holds up. Most of the time System 1 is good enough. The trouble is that it does not notice when it is wrong. Kahneman calls this habit "what you see is all there is". System 1 builds the best story it can from the information it has, and it does not ask what is missing.

Genie Agent mode now offers a similar choice. If you switch on the lightning button next to Agent, you get [Flash](https://docs.databricks.com/aws/en/ai-bi/release-notes/2026), which spends less time reasoning and answers faster. If you leave it off, you get standard Agent mode, which takes longer and checks more. I will call them Flash and Standard.

[IMAGE: screenshots/01-flash-toggle.png]
Alt text: The Genie agent "Meridian Parcel Operations" with a question typed in. Agent is selected and the lightning button for Flash is switched on.

Databricks [recommends Flash for simpler tasks](https://docs.databricks.com/aws/en/genie-agents/concepts). But that volume question looks simple, and nothing in it says that half of October is missing. So I wanted a practical answer. When is the fast answer enough, and when should I wait for the slow one?

## How I tested it

I made up a delivery company called Meridian Parcel and hid traps in its data. Each trap is a number that points the wrong way at first glance, plus one check that shows the truth. These are some of the traps:

- A month of data stops halfway.
- Every row for a month was loaded twice.
- An average falls only because the mix of parcels changed.

For each trap, I also built a control network where the first number is correct. A good answer should not invent a problem there.

I asked about each network in three ways:

- A lookup asks for a figure, e.g., the average delivery time in each month.
- A directed question names the check, e.g., it asks for volume per day.
- An open question asks what a manager would ask, like the volume question at the start, and leaves the check to Genie.

I ran the test in two rounds. The first round used four everyday cases, such as an average that falls only because the mix of parcels changed. After seeing the results, I built a second round with four harder traps that the agent's instructions never mention, such as the half month of data. I asked every question five times in each mode, each time in a fresh conversation, for 480 answers in all.

Before each round, I wrote down what a correct answer had to contain. Another AI model graded every answer against that list without knowing which mode wrote it, and I checked a sample by hand. After a review, I fixed two mistakes in my first round list and regraded every answer. I also settled a few uneven grades by hand. The [change log](https://github.com/Praneeth16/genie-flash-vs-standard/blob/main/notes/key_changes.md) lists each change.

## When fast is enough

When the question named the check, Flash did almost as well as Standard. Both reached the right conclusion in all 40 directed responses in the first round. In the second round, Flash got 38 of 40 and Standard got 40. On first round lookups, Flash was perfect at 40 of 40.

This fits Kahneman's picture. System 1 does fine when someone points it at the right thing. If I ask Genie for volume per day, Flash computes volume per day. It does not need to work out that it should.

[IMAGE: figures/fig2-pass-by-level.png]
Alt text: Dot chart of first round answers that met every check, by question type. Lookup: Flash 40/40, Standard 39/40. Directed: Flash 36/40, Standard 40/40. Open: Flash 26/40, Standard 37/40.

In the first round, the gap on directed questions came from detail. Flash sometimes gave the right answer without the numbers behind it. In the second round, one of its misses was stranger. Flash found that the complaint rate in remote deliveries fell from 8% to 7%, and then wrote that it had "nearly quadrupled".

## When the obvious number is wrong

The open questions are where the two modes split. In the second round, Flash reached the right conclusion on the partial month, duplicate and mix traps in 0 of 15 runs. Standard reached it in 10.

Flash usually ran one query and reported what it saw. When every October row had been loaded twice, Flash said volume "doubled" in all five runs. When a complaint rate rose overall but fell in both delivery zones, Flash said it got worse in all five runs. This is "what you see is all there is" in practice. The first query returns a plausible number, and nothing in the number says it is wrong.

Standard ran more queries before it answered. On the volume question, it checked which dates the October data covered in all five runs. On a delivery question in the first round, it split parcels into local and remote and found that both got slower, in four of five runs. The overall average had fallen from 6.8 days to 4.2 only because October shipped far more local parcels, which are quick to deliver.

[IMAGE: figures/anim-mix-shift.gif]
Alt text: Animation of 1,000 parcels. The local share grows from 20% to 80% while local and remote delivery times each rise by one day. The overall average moves from 6.8 days down to 4.2 days.

[IMAGE: figures/fig5-round2-open.png]
Alt text: Dot chart of second round open answers that reached the full conclusion. Half of October missing: Flash 0/5, Standard 5/5. October rows loaded twice: Flash 0/5, Standard 2/5. Complaint rate with a change in zone mix: Flash 0/5, Standard 3/5. The control for the zone mix trap: both 0/5. The other controls and the internal test parcel trap: both 5/5.

The checks cost time. On the open questions in the second round, Flash took a median of 11 seconds and Standard took 26.

## Slow is not always right

Standard got 10 of those 15 trap runs right, not 15. It found the duplicate rows in only two of five runs.

It also overthought. One lookup asked only for two averages, and Standard added "Delivery time improved by 2.6 days month-over-month", which is the misreading the trap was built to catch. On a control where the complaint rate did get worse, Standard twice ran a significance test and declined to call it worse. The other answers, from both modes, said it got worse but never checked the two zones, which my list required. That is why the chart shows 0 of 5 for both.

Standard also wrote more. Its median open answer in the first round had 233 words, against 63 for Flash. In those open answers, the grading model found 25 claims that the data did not support in Standard's answers, against 8 in Flash's. More reasoning gave Standard more room to be useful and more room to be wrong.

## So which one should you use?

Here is how I plan to choose:

- If I can name the check, I use Flash and put the check in the question. I also ask for the supporting numbers, because Flash tends to leave them out.
- If the obvious number could be wrong for a reason I have not thought of, I use Standard. Partial months, duplicate rows and shifts in mix are the cases where Flash failed in every open run.

In Kahneman's terms, Flash behaves like System 1, and the person asking can do the System 2 part. When you know what could go wrong, you can write the check into the question and get the fast answer. When you don't know what could go wrong, wait for Standard to look.

If you build Genie agents, you can also write the checks your users often need into the agent's instructions, e.g., checking that a month is complete. Flash might then make them too. I have not tested that yet.

## What this test can't tell you

The data is small and made up, and each trap has one designed check. The open questions are a small sample, so the size of the gap is uncertain, although Standard led in both rounds. One AI model graded every answer. I measured time, not cost. Flash is in Beta, so these results describe one day, 31 October 2026.

The data, questions, runner, raw responses and grades are in [github.com/Praneeth16/genie-flash-vs-standard](https://github.com/Praneeth16/genie-flash-vs-standard), so you can run the same test on your own Genie agent.

## Sources

1. Daniel Kahneman. Thinking, Fast and Slow. Farrar, Straus and Giroux, 2011.
2. [Databricks. AI/BI and Genie release notes 2026 (15 October 2026: Flash Beta).](https://docs.databricks.com/aws/en/ai-bi/release-notes/2026)
3. [Databricks. Genie Agents concepts (Flash and standard Agent mode).](https://docs.databricks.com/aws/en/genie-agents/concepts)

*I work at Databricks. Opinions here are my own. All data in this article is made up.*
