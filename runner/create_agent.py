"""Create (or update) the Meridian Parcel Genie agent. Prints the space ID."""
import hashlib, json, os, sys
from databricks.sdk import WorkspaceClient

PROFILE = os.environ.get("DATABRICKS_CONFIG_PROFILE")
WAREHOUSE = os.environ["WAREHOUSE_ID"]
FQ = os.environ.get("MERIDIAN_CATALOG", "serverless_lakebase_praneeth_catalog") + ".meridian_parcel"
TABLES = ["complaints", "credits", "invoices", "networks", "refund_policies", "routing_changes", "shipments"]

INSTRUCTIONS = [
    "Meridian Parcel is a parcel delivery company. Each distribution network has a network_id such as NW-1234.\n",
    "A shipment belongs to the month of its ship_date. Delivery time means delivery_days.\n",
    "Complaint rate means complaints opened in a month divided by shipments shipped in that month, in the same network.\n",
    "Net contribution means invoice revenue minus fulfilment_cost minus credits. Credits link to invoices through invoice_id. An invoice belongs to the month of its invoice_date.\n",
    "Late-delivery refunds: the refund policy in effect on a shipment's promised_date applies. A shipment qualifies when delay_days is greater than the policy's min_delay_days_exclusive and its delay_reason is not the policy's excluded_delay_reason. The refund is the shipment's shipping_fee.\n",
]

def jid(name):
    return hashlib.md5(name.encode()).hexdigest()

def join(left, right, cond, rt):
    return {"id": jid(left + right), "left": {"identifier": f"{FQ}.{left}", "alias": left},
            "right": {"identifier": f"{FQ}.{right}", "alias": right},
            "sql": [cond, f"--rt=FROM_RELATIONSHIP_TYPE_{rt}--"]}

space = {
    "version": 2,
    "data_sources": {"tables": [{"identifier": f"{FQ}.{t}"} for t in TABLES]},
    "instructions": {
        "text_instructions": [{"id": jid("definitions"), "content": INSTRUCTIONS}],
        "join_specs": sorted([
            join("shipments", "networks", "`shipments`.`network_id` = `networks`.`network_id`", "MANY_TO_ONE"),
            join("complaints", "shipments", "`complaints`.`shipment_id` = `shipments`.`shipment_id`", "MANY_TO_ONE"),
            join("credits", "invoices", "`credits`.`invoice_id` = `invoices`.`invoice_id`", "MANY_TO_ONE"),
        ], key=lambda j: j["id"]),
    },
}

w = WorkspaceClient(profile=PROFILE)
body = {"title": "Meridian Parcel Operations", "warehouse_id": WAREHOUSE,
        "description": "Shipments, complaints, invoices, credits and refund policies for Meridian Parcel networks.",
        "serialized_space": json.dumps(space)}
if len(sys.argv) > 1:
    r = w.api_client.do("PATCH", f"/api/2.0/genie/spaces/{sys.argv[1]}", body=body)
else:
    r = w.api_client.do("POST", "/api/2.0/genie/spaces", body=body)
print(r["space_id"])
print("config_sha256", hashlib.sha256(body["serialized_space"].encode()).hexdigest())
