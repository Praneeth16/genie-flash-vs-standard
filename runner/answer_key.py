"""28 questions, criteria and facts. The agent never sees this file. Writes answer_key.json."""
import json
from pathlib import Path

NO_UNSUPPORTED = "Makes no claim that the data does not support, such as an invented cause, number or comparison."

CASES = {
    "delivery": {
        "reversal": {"network": "NW-4127", "facts": "Shipment month = month of ship_date. Overall average delivery_days: Sep 6.8, Oct 4.2. Local: Sep 2.0, Oct 3.0. Remote: Sep 8.0, Oct 9.0. Local share of shipments: Sep 20% (200 of 1,000), Oct 80% (800 of 1,000). Late rate (delay_days > 0) rose from 0% to 50% in both zones. The overall average fell only because the mix shifted to local parcels. Delivery got slower in both zones.",
                     "conclusion": "States that delivery performance did not really improve: the overall average fell because of the shift to local parcels, while both zones got slower."},
        "control": {"network": "NW-2863", "facts": "Overall average delivery_days: Sep 6.8, Oct 5.8. Local: Sep 2.0, Oct 1.0. Remote: Sep 8.0, Oct 7.0. Local share 20% in both months (200 of 1,000). Mix is unchanged, both zones got faster. The headline improvement is real.",
                    "conclusion": "States that delivery performance improved, and that the segment trends support the headline (both zones faster, mix unchanged)."},
        "lookup": "What was the average delivery time for network {n} shipments shipped in September 2026 and in October 2026?",
        "directed": "For network {n}, compare September and October 2026 on three things: the overall average delivery time, the average delivery time in each service zone, and each zone's share of shipments. What do these comparisons show?",
        "open": "Did delivery performance in network {n} improve from September to October 2026? Support your conclusion.",
        "lookup_criteria": ["States the September average as {sep} days.", "States the October average as {oct} days.", "Scopes the numbers to network {n} and to shipments grouped by ship month."],
        "full_criteria": ["Reports the overall average delivery time for both months correctly ({sep} and {oct} days).", "Reports the average for each service zone in both months correctly (local {lsep} to {loct}, remote {rsep} to {roct}).", "Reports each zone's share of shipments (local {ssep} to {soct}) and explains how the mix affects the overall average."],
        "values": {"reversal": dict(sep="6.8", oct="4.2", lsep="2.0", loct="3.0", rsep="8.0", roct="9.0", ssep="20%", soct="80%"),
                   "control": dict(sep="6.8", oct="5.8", lsep="2.0", loct="1.0", rsep="8.0", roct="7.0", ssep="20%", soct="20%")},
    },
    "complaints": {
        "reversal": {"network": "NW-7351", "facts": "Complaints opened: Sep 40, Oct 60. Shipments shipped: Sep 1,000, Oct 2,000. Complaint rate: Sep 4.0%, Oct 3.0%. Count rose but the rate fell because volume doubled.",
                     "conclusion": "States that complaints did not get worse per shipment: the count rose because volume doubled, and the complaint rate fell."},
        "control": {"network": "NW-1594", "facts": "Complaints opened: Sep 40, Oct 60. Shipments shipped: Sep 1,000, Oct 1,000. Complaint rate: Sep 4.0%, Oct 6.0%. Count and rate both rose.",
                    "conclusion": "States that complaints got worse, because both the count and the rate rose."},
        "lookup": "How many complaints were opened in network {n} in September 2026 and in October 2026?",
        "directed": "For network {n}, compare September and October 2026 on complaint count and complaint rate (complaints per shipment). What do they show?",
        "open": "Are complaints getting worse in network {n} from September to October 2026? Support your conclusion.",
        "lookup_criteria": ["States 40 complaints in September.", "States 60 complaints in October.", "Scopes the counts to network {n} and to the month the complaint was opened."],
        "full_criteria": ["Reports complaint counts correctly (40 in September, 60 in October).", "Reports shipment volume correctly ({vsep} in September, {voct} in October).", "Reports the complaint rate correctly ({rsep} in September, {roct} in October)."],
        "values": {"reversal": dict(vsep="1,000", voct="2,000", rsep="4.0%", roct="3.0%"),
                   "control": dict(vsep="1,000", voct="1,000", rsep="4.0%", roct="6.0%")},
    },
    "contribution": {
        "reversal": {"network": "NW-6208", "facts": "Invoice grain: Sep revenue $100,000, cost $70,000, credits $0. Oct revenue $120,000, cost $80,000, credits $20,000 (4 invoices with 2 credit rows each). Net contribution: Sep $30,000, Oct $20,000. A raw join of invoices to credits wrongly shows Oct revenue $160,000 and net $33,000. Revenue minus cost alone rises $30,000 to $40,000.",
                     "conclusion": "States that net contribution fell (from $30,000 to $20,000), so the network became less profitable even though revenue rose."},
        "control": {"network": "NW-3916", "facts": "Invoice grain: Sep revenue $100,000, cost $70,000, credits $0. Oct revenue $120,000, cost $80,000, credits $5,000 (2 invoices with 2 credit rows each). Net contribution: Sep $30,000, Oct $35,000. A raw join wrongly shows Oct revenue $140,000 and net $41,500.",
                    "conclusion": "States that the network became more profitable: net contribution rose from $30,000 to $35,000 after credits."},
        "lookup": "What was total invoiced revenue for network {n} in September 2026 and in October 2026?",
        "directed": "For network {n}, calculate net contribution (revenue minus fulfilment cost minus credits) for September and October 2026. Count each invoice once, even when it has several credit rows. Did net contribution rise?",
        "open": "Did network {n} become more profitable from September to October 2026? Support your conclusion.",
        "lookup_criteria": ["States September revenue as $100,000.", "States October revenue as $120,000 (not a duplicated figure such as $140,000 or $160,000).", "Scopes the revenue to network {n} and to invoice month."],
        "full_criteria": ["Reports revenue and fulfilment cost correctly for both months without duplicating invoices ($100,000 and $70,000 in September, $120,000 and $80,000 in October).", "Includes every credit: $0 in September and {coct} in October.", "Reports net contribution correctly ($30,000 in September, {noct} in October)."],
        "values": {"reversal": dict(coct="$20,000", noct="$20,000"), "control": dict(coct="$5,000", noct="$35,000")},
    },
    "refunds": {
        "reversal": {"network": "NW-5472", "facts": "8 shipments promised in October were late (delay_days > 0). Policy is chosen by promised_date: v1 (to 2026-10-14) needs delay_days > 5, v2 (from 2026-10-15) needs delay_days > 3. Weather never qualifies. Eligible: SH-NW-5472-L-R02 (v1, 6 days), R04 (v2, 4 days), R07 (v2, 5 days) = 3 shipments, $60. Traps: R01 promised Oct 12 (v1) delayed 4 but delivered after Oct 15; R03 v1 delayed exactly 5; R06 v2 delayed exactly 3; R05 and R08 weather.",
                     "conclusion": "States 3 qualifying shipments and $60 total refund."},
        "control": {"network": "NW-8045", "facts": "8 shipments promised in October were late. All 8 late shipments have promised dates on or after 2026-10-15, so v2 (delay_days > 3) applies to each of them. The on-time shipments span both policies but cannot qualify because they are not late. Weather excluded. Eligible: C01 to C06 = 6 shipments, $120. C07 is weather, C08 delayed exactly 3.",
                    "conclusion": "States 6 qualifying shipments and $120 total refund."},
        "lookup": "How many network {n} shipments with a promised date in October 2026 were delivered late?",
        "directed": "For network {n} shipments with a promised date in October 2026, apply the refund policy in effect on each shipment's promised date, including its delay threshold and weather exclusion. How many shipments qualify, and what is the total refund?",
        "open": "What will late-delivery refunds cost for network {n} shipments with a promised date in October 2026?",
        "lookup_criteria": ["States 8 late shipments.", "Treats late as delivered after the promised date (delay_days greater than 0).", "Scopes the count to network {n} and to promised dates in October 2026."],
        "full_criteria": ["Selects the policy by each shipment's promised date ({policy}).", "Applies the strict threshold (greater than, not greater than or equal) and excludes weather delays.", "Identifies the correct number of qualifying shipments ({k})."],
        "values": {"reversal": dict(policy="v1 for promised dates up to 14 October, v2 from 15 October", k="3"),
                   "control": dict(policy="v2 for every late shipment, because every late shipment was promised on or after 15 October", k="6")},
    },
}

MISSING = [
    ("routing", "NW-2863", "Did the routing change in network NW-2863 on 1 October 2026 cause its faster deliveries? How many days did it save?",
     "routing_changes has one row: NW-2863 changed routing on 2026-10-01 for the whole network. Delivery time fell 6.8 to 5.8 days (both zones 1 day faster). No comparison group, no randomization and only one month before the change. Causation cannot be established.",
     ["Reports the observed change correctly (6.8 to 5.8 days overall, or about 1 day faster in each zone) as an observation.",
      "States that the data cannot establish that the routing change caused the improvement, and gives a reason (for example no comparison group or holdout, a single network and date, or other changes at the same time).",
      "Does not present a causal number of days saved as an established fact.",
      "Names evidence that would be needed to test causation, such as a comparison network, a holdout, a longer pre-period or a staggered rollout."]),
    ("unreported", "NW-1594", "How many customers in network NW-1594 had a problem with an October 2026 delivery but never filed a complaint?",
     "The data records only complaints that customers filed (60 in October for NW-1594). It has no survey, contact or problem data for customers who did not complain.",
     ["States that the data cannot count customers who had a problem but did not complain.",
      "Explains why: the tables only record filed complaints.",
      "Does not present an invented or estimated number as the answer.",
      "Labels any proxy (for example late deliveries without a complaint) clearly as a proxy, or suggests the evidence that would be needed."]),
    ("november", "NW-4127", "What was the average delivery time for network NW-4127 shipments shipped in November 2026?",
     "No shipment in the data has a ship_date in November 2026. The latest ship_date is 2026-10-28. NW-4127 shipments end on 2026-10-20.",
     ["States that the data has no November 2026 shipments for this network.",
      "Supports this with the data coverage (for example the latest ship date in the data).",
      "Does not present a number as the November average.",
      "Labels any estimate or the October figure clearly as not a November observation."]),
    ("paid", "NW-5472", "How much did we actually pay out in late-delivery refunds for network NW-5472 in October 2026?",
     "The data has no refund payment or transaction table. It can only estimate eligible refunds: 3 shipments, $60, under the policy rules.",
     ["States that the data has no record of refunds actually paid.",
      "Does not present the eligible amount as the amount paid.",
      "If it gives an eligibility estimate, the estimate is correct (3 shipments, $60) and labelled as eligibility; giving no estimate also passes.",
      "Names the evidence needed, such as refund payment or transaction records. Stating that payment records are missing from the data counts."]),
]

def build():
    qs = []
    for case, c in CASES.items():
        for version in ("reversal", "control"):
            v = c[version]
            n = v["network"]
            vals = {**c["values"][version], "n": n}
            for level in ("lookup", "directed", "open"):
                if level == "lookup":
                    crit = [x.format(**vals) for x in c["lookup_criteria"]] + [NO_UNSUPPORTED]
                else:
                    crit = [x.format(**vals) for x in c["full_criteria"]] + [v["conclusion"]]
                qs.append({"qid": f"{case}-{version}-{level}", "case": case, "version": version, "level": level,
                           "network": n, "question": c[level].format(n=n), "criteria": crit, "facts": v["facts"]})
    for name, n, q, facts, crit in MISSING:
        qs.append({"qid": f"missing-{name}", "case": "missing", "version": "missing", "level": "missing",
                   "network": n, "question": q, "criteria": crit, "facts": facts})
    assert len(qs) == 28 and all(len(q["criteria"]) == 4 for q in qs)
    return qs

if __name__ == "__main__":
    out = Path(__file__).with_name("answer_key.json")
    out.write_text(json.dumps(build(), indent=1))
    print(out, len(build()))
