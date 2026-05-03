import awswrangler as wr
import pandas as pd
import os
import logging

logger = logging.getLogger(__name__)

DATABASE  = os.getenv("ATHENA_DATABASE",  "glue_datalake")
S3_OUTPUT = os.getenv("ATHENA_S3_OUTPUT", "s3://peliculas-datalake/athena-results/")


def run_query(sql: str) -> list[dict]:
    """
    Ejecuta una consulta SQL en Athena y devuelve los resultados como lista de dicts.
    Lanza RuntimeError si algo falla.
    """
    logger.info(f"▶ Ejecutando query Athena:\n{sql}")
    try:
        df: pd.DataFrame = wr.athena.read_sql_query(
            sql=sql,
            database=DATABASE,
            s3_output=S3_OUTPUT,
            ctas_approach=False,
        )
        return df.to_dict(orient="records")
    except Exception as e:
        logger.error(f"❌ Error en Athena: {e}")
        raise RuntimeError(str(e))