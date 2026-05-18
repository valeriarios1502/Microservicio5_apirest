import boto3
import os
import time
import logging

logger = logging.getLogger(__name__)

DATABASE  = os.getenv("ATHENA_DATABASE")
S3_OUTPUT = os.getenv("ATHENA_S3_OUTPUT")
AWS_REGION = os.getenv("AWS_REGION")

athena = boto3.client("athena", region_name=AWS_REGION)


def run_query(sql: str) -> list[dict]:
    logger.info(f"Ejecutando query Athena:\n{sql}")

    response = athena.start_query_execution(
        QueryString=sql,
        QueryExecutionContext={"Database": DATABASE},
        ResultConfiguration={"OutputLocation": S3_OUTPUT},
    )
    query_id = response["QueryExecutionId"]

    for _ in range(60):  
        status_resp = athena.get_query_execution(QueryExecutionId=query_id)
        state = status_resp["QueryExecution"]["Status"]["State"]

        if state == "SUCCEEDED":
            break
        elif state in ("FAILED", "CANCELLED"):
            reason = status_resp["QueryExecution"]["Status"].get("StateChangeReason", "")
            raise RuntimeError(f"Query Athena {state}: {reason}")

        time.sleep(1)
    else:
        raise RuntimeError("Query Athena timeout")

    results = athena.get_query_results(QueryExecutionId=query_id)
    rows = results["ResultSet"]["Rows"]

    if not rows:
        return []

    columns = [col["VarCharValue"] for col in rows[0]["Data"]]
    data = []
    for row in rows[1:]:
        data.append({
            columns[i]: cell.get("VarCharValue", None)
            for i, cell in enumerate(row["Data"])
        })
    return data
