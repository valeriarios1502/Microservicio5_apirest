from fastapi import APIRouter, HTTPException, Query
from client import run_query

router = APIRouter()


@router.get("/por-pais", summary="Usuarios agrupados por país")
def usuarios_por_pais():
    """
    Devuelve el conteo de usuarios por país, ordenado de mayor a menor.
    """
    sql = """
        SELECT pais, COUNT(*) AS total_usuarios
        FROM glue_datalake.usuarios
        GROUP BY pais
        ORDER BY total_usuarios DESC
    """
    try:
        return {"data": run_query(sql)}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/peliculas-vistas-top", summary="Usuarios con más películas vistas")
def usuarios_peliculas_vistas(
    limit: int = Query(default=10, ge=1, le=100)
):
    """
    Lista los usuarios que han marcado más películas como vistas.
    """
    sql = f"""
        SELECT u.id AS usuario_id, u.name AS nombre, u.pais,
               COUNT(pv.pelicula_id) AS peliculas_vistas
        FROM glue_datalake.usuarios u
        LEFT JOIN glue_datalake.peliculas_vistas pv ON u.id = pv.usuario_id
        GROUP BY u.id, u.name, u.pais
        ORDER BY peliculas_vistas DESC
        LIMIT {limit}
    """
    try:
        return {"data": run_query(sql)}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/resumen", summary="Resumen estadístico de usuarios")
def resumen_usuarios():
    """
    Estadísticas generales: total de usuarios, países únicos.
    """
    sql = """
        SELECT
            COUNT(*)           AS total_usuarios,
            COUNT(DISTINCT pais) AS paises_unicos
        FROM glue_datalake.usuarios
    """
    try:
        return {"data": run_query(sql)}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))