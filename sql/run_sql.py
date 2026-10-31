"""Run a SQL file statement by statement in meridian_parcel. Usage: run_sql.py FILE"""
import os, sys
from databricks.sdk import WorkspaceClient

PROFILE = os.environ.get("DATABRICKS_CONFIG_PROFILE")
WAREHOUSE = os.environ["WAREHOUSE_ID"]
CATALOG, SCHEMA = os.environ.get("MERIDIAN_CATALOG", "serverless_lakebase_praneeth_catalog"), "meridian_parcel"

w = WorkspaceClient(profile=PROFILE)
text = "\n".join(l for l in open(sys.argv[1]).read().splitlines() if not l.strip().startswith("--"))
for stmt in [s.strip() for s in text.split(";") if s.strip()]:
    r = w.statement_execution.execute_statement(
        statement=stmt, warehouse_id=WAREHOUSE, catalog=CATALOG,
        schema=SCHEMA if "CREATE SCHEMA" not in stmt else None, wait_timeout="50s")
    state = r.status.state.value
    print(state, stmt.splitlines()[0][:90])
    if state != "SUCCEEDED":
        print(r.status.error)
        sys.exit(1)
    if r.result and r.result.data_array and stmt.upper().startswith(("SELECT", "WITH")):
        cols = [c.name for c in r.manifest.schema.columns]
        print(" | ".join(cols))
        for row in r.result.data_array:
            print(" | ".join(str(x) for x in row))
