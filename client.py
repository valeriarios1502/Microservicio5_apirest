import boto3
import os
import time
import logging

logger = logging.getLogger(__name__)

DATABASE  = os.getenv("ATHENA_DATABASE",  "glue_datalake")
S3_OUTPUT = os.getenv("ATHENA_S3_OUTPUT", "s3://peliculas-datalake/athena-results/")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

athena = boto3.client("athena", region_name=AWS_REGION)


def run_query(sql: str) -> list[dict]:
    """
    Ejecuta una consulta SQL en Athena con boto3 puro
    y devuelve los resultados como lista de dicts.
    """
    logger.info(f"▶ Ejecutando query Athena:\n{sql}")

    # 1. Lanzar la query
    response = athena.start_query_execution(
        QueryString=sql,
        QueryExecutionContext={"Database": DATABASE},
        ResultConfiguration={"OutputLocation": S3_OUTPUT},
    )
    query_id = response["QueryExecutionId"]

    # 2. Esperar resultado
    for _ in range(60):  # máximo 60 segundos
        status_resp = athena.get_query_execution(QueryExecutionId=query_id)
        state = status_resp["QueryExecution"]["Status"]["State"]

        if state == "SUCCEEDED":
            break
        elif state in ("FAILED", "CANCELLED"):
            reason = status_resp["QueryExecution"]["Status"].get("StateChangeReason", "")
            raise RuntimeError(f"Query Athena {state}: {reason}")

        time.sleep(1)
    else:
        raise RuntimeError("Query Athena timeout después de 60 segundos")

    # 3. Obtener resultados
    results = athena.get_query_results(QueryExecutionId=query_id)
    rows = results["ResultSet"]["Rows"]

    if not rows:
        return []

    # Primera fila = headers
    columns = [col["VarCharValue"] for col in rows[0]["Data"]]
    data = []
    for row in rows[1:]:
        data.append({
            columns[i]: cell.get("VarCharValue", None)
            for i, cell in enumerate(row["Data"])
        })

    logger.info(f"✅ {len(data)} filas obtenidas")
    return data
