"""Round 2: 20 questions, four criteria each. Written and committed before the run. Writes answer_key_r2.json.
Part A (agent "nodefs"): round 1 complaint and refund open questions, asked of an agent whose instructions
do not define complaint rate or refund eligibility. Same criteria as round 1.
Part B (agent "r2"): four traps the agent instructions never mention, each with a control, at directed and open level."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
R1 = {q["qid"]: q for q in json.loads((HERE / "answer_key.json").read_text())}

VOLUME_OPEN = "How did shipment volume in network {n} change from September to October 2026? Support your conclusion."

TRAPS = {
    "partial": {
        "directed": "For network {n}, compare shipment volume in September and October 2026. Check which dates each month's data covers, and compare shipments per day. Did volume fall?",
        "open": VOLUME_OPEN,
        "reversal": {"network": "NW-6731",
                     "facts": "September: 900 shipments shipped 1 to 30 September (30 per day). October: 600 shipments, but October data for NW-6731 ends on 15 October (40 per day). 1 to 15 September had 450 shipments. Other networks have October data to the end of the month. On a comparable basis volume rose by a third.",
                     "criteria": ["Reports 900 shipments in September and 600 in October.",
                                  "States that NW-6731's October data ends on 15 October, or that it covers only half the month.",
                                  "Compares on a like-for-like basis, e.g., 30 versus 40 shipments per day, or 450 versus 600 shipments in the first 15 days.",
                                  "Concludes that volume did not fall on a comparable basis (it rose), and that the October total is incomplete."]},
        "control": {"network": "NW-2290",
                    "facts": "September: 900 shipments over 30 days (30 per day). October: 600 shipments over 1 to 31 October (about 19.4 per day). Both months are complete. Volume really fell by a third.",
                    "criteria": ["Reports 900 shipments in September and 600 in October.",
                                 "States that October data covers the whole month, to 31 October.",
                                 "Compares shipments per day or otherwise confirms the months are comparable (30 versus about 19.4 per day).",
                                 "Concludes that volume fell."]},
    },
    "duplicate": {
        "directed": "For network {n}, compare shipment volume in September and October 2026. Check for shipment_id values that appear more than once, and count each shipment once. Did volume grow?",
        "open": VOLUME_OPEN,
        "reversal": {"network": "NW-9154",
                     "facts": "September: 1,000 shipments. October: 2,000 rows but only 1,000 distinct shipment_id values. Every October shipment was written twice, by loads B-202610 and B-202610-reload. Volume was flat.",
                     "criteria": ["Reports September volume as 1,000 shipments.",
                                  "Identifies that October rows are duplicated: each of 1,000 shipments appears twice, from two loads.",
                                  "Reports October volume as 1,000 distinct shipments.",
                                  "Concludes that volume stayed flat and that the apparent doubling comes from the duplicate load."]},
        "control": {"network": "NW-4486",
                    "facts": "September: 1,000 shipments. October: 2,000 distinct shipments from one load. No shipment_id appears twice. Volume really doubled.",
                    "criteria": ["Reports September volume as 1,000 shipments.",
                                 "Confirms that no shipment_id appears twice, or counts distinct shipments and gets the same totals.",
                                 "Reports October volume as 2,000 distinct shipments.",
                                 "Concludes that volume doubled."]},
    },
    "testparcels": {
        "directed": "For network {n}, compare the average delivery time in September and October 2026 for customer shipments only, leaving out internal test parcels (is_test). Did delivery time improve?",
        "open": "Did delivery performance in network {n} improve from September to October 2026? Support your conclusion.",
        "reversal": {"network": "NW-3378",
                     "facts": "September: 1,000 customer shipments, average 5.0 days, no test parcels. October: 1,000 customer shipments averaging 5.5 days plus 1,000 one-day test parcels (is_test TRUE). The average over all rows falls from 5.0 to 3.25 days. Customer delivery got slower.",
                     "criteria": ["Identifies the test parcels: 1,000 in October and none in September.",
                                  "Reports the customer-only average for both months, 5.0 and 5.5 days.",
                                  "Explains that the test parcels pull the October average over all rows down to 3.25 days.",
                                  "Concludes that delivery for customers got slower, not faster."]},
        "control": {"network": "NW-7712",
                    "facts": "Each month has 100 one-day test parcels. Customer shipments average 5.0 days in September and 4.0 in October. The average over all rows falls from 4.64 to 3.73. The improvement is real.",
                    "criteria": ["Identifies the test parcels: 100 in each month.",
                                 "Reports the customer-only average for both months, 5.0 and 4.0 days.",
                                 "Shows that the improvement holds without the test parcels.",
                                 "Concludes that delivery improved."]},
    },
    "zonemix": {
        "directed": "For network {n}, compare the complaint rate in September and October 2026 overall and within each service zone, and each zone's share of shipments. What do they show?",
        "open": "Is the complaint rate in network {n} getting worse from September to October 2026? Support your conclusion.",
        "reversal": {"network": "NW-5809",
                     "facts": "Overall complaint rate: 32 of 1,000 (3.2%) in September, 58 of 1,000 (5.8%) in October. Local: 2% to 1%. Remote: 8% to 7%. Local share of shipments: 80% to 20%. Remote parcels draw more complaints, so the mix shift raises the overall rate while both zones improve.",
                     "criteria": ["Reports the overall complaint rate, 3.2% in September and 5.8% in October.",
                                  "Reports the rate in each zone: local 2% to 1%, remote 8% to 7%.",
                                  "Reports the zone mix shift (local share 80% to 20%) and explains that it raises the overall rate.",
                                  "Concludes that the complaint rate improved within each zone, and that the overall rise comes from the shift toward remote parcels."]},
        "control": {"network": "NW-1263",
                    "facts": "Overall complaint rate: 3.2% in September, 4.4% in October. Local: 2% to 3%. Remote: 8% to 10%. Local share 80% in both months. The rate got worse in both zones.",
                    "criteria": ["Reports the overall complaint rate, 3.2% in September and 4.4% in October.",
                                 "Reports the rate in each zone: local 2% to 3%, remote 8% to 10%.",
                                 "Reports that the zone mix did not change (local 80% in both months).",
                                 "Concludes that the complaint rate got worse in both zones."]},
    },
}

def build():
    qs = []
    for qid in ["complaints-reversal-open", "complaints-control-open", "refunds-reversal-open", "refunds-control-open"]:
        q = dict(R1[qid])
        q.update(qid=f"nodefs-{qid}", agent="nodefs", level="nodefs")
        qs.append(q)
    for case, t in TRAPS.items():
        for version in ("reversal", "control"):
            v = t[version]
            for level in ("directed", "open"):
                qs.append({"qid": f"{case}-{version}-{level}", "agent": "r2", "case": case, "version": version, "level": level,
                           "network": v["network"], "question": t[level].format(n=v["network"]),
                           "criteria": v["criteria"], "facts": v["facts"]})
    assert len(qs) == 20 and all(len(q["criteria"]) == 4 for q in qs)
    return qs

if __name__ == "__main__":
    out = HERE / "answer_key_r2.json"
    out.write_text(json.dumps(build(), indent=1))
    print(out, len(build()))
