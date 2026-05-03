from fastapi import APIRouter, HTTPException, Query
from client import run_query

router = APIRouter()


@router.get("/mas-activos", summary="Top 10 foros con más mensajes")
def foros_mas_activos():
    """
    Devuelve los 10 hilos/foros con mayor cantidad de mensajes.
    """
    sql = """
        SELECT
            threadid    AS foro_id,
            COUNT(id)   AS total_mensajes
        FROM glue_datalake.messages
        GROUP BY threadid
        ORDER BY total_mensajes DESC
        LIMIT 10
    """
    try:
        return {"data": run_query(sql)}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/actividad", summary="Vista actividad de foros (con título y votos)")
def actividad_foros(
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    """
    Usa la vista `vista_foros_actividad` para mostrar foros con su título,
    película asociada, votos y total de mensajes.
    """
    sql = f"""
        SELECT foro_id, titulo, pelicula_id, votos, total_mensajes
        FROM glue_datalake.vista_foros_actividad
        ORDER BY total_mensajes DESC
        LIMIT {limit} OFFSET {offset}
    """
    try:
        return {"data": run_query(sql), "limit": limit, "offset": offset}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/resumen", summary="Resumen general de foros y mensajes")
def resumen_foros():
    """
    Estadísticas globales: total de threads, total de mensajes, promedio por foro.
    """
    sql = """
        SELECT
            COUNT(DISTINCT threadid)        AS total_foros,
            COUNT(id)                       AS total_mensajes,
            ROUND(AVG(mensajes_por_foro), 2) AS promedio_mensajes_por_foro
        FROM (
            SELECT threadid, COUNT(id) AS mensajes_por_foro
            FROM glue_datalake.messages
            GROUP BY threadid
        ) sub
    """
    try:
        return {"data": run_query(sql)}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/por-pelicula/{movie_id}", summary="Foros relacionados a una película")
def foros_por_pelicula(movie_id: int):
    """
    Lista los foros (threads) vinculados a una película específica.
    """
    sql = f"""
        SELECT foro_id, titulo, votos, total_mensajes
        FROM glue_datalake.vista_foros_actividad
        WHERE pelicula_id = {movie_id}
        ORDER BY total_mensajes DESC
    """
    try:
        resultado = run_query(sql)
        if not resultado:
            raise HTTPException(status_code=404, detail=f"No se encontraron foros para movie_id={movie_id}")
        return {"data": resultado}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))