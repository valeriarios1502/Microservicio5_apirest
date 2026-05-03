from fastapi import APIRouter, HTTPException, Query
from athena_client import run_query

router = APIRouter()


@router.get("/top-calificadas", summary="Top 10 películas mejor calificadas")
def top_peliculas_calificadas():
    """
    Devuelve las 10 películas con mayor rating del datalake.
    """
    sql = """
        SELECT id, title, year, rating
        FROM glue_datalake.movies
        ORDER BY rating DESC
        LIMIT 10
    """
    try:
        return {"data": run_query(sql)}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/completa", summary="Vista completa de películas (con género y director)")
def peliculas_completa(
    limit: int = Query(default=50, ge=1, le=500, description="Máximo de registros a devolver"),
    offset: int = Query(default=0, ge=0, description="Registros a saltear (paginación)"),
):
    """
    Retorna películas enriquecidas con género y director usando la vista
    `vista_peliculas_completa`.
    """
    sql = f"""
        SELECT movie_id, title, year, rating, genero, director
        FROM glue_datalake.vista_peliculas_completa
        ORDER BY rating DESC
        LIMIT {limit} OFFSET {offset}
    """
    try:
        return {"data": run_query(sql), "limit": limit, "offset": offset}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/actores-top", summary="Top 10 actores con más películas")
def actores_top():
    """
    Devuelve los 10 actores que aparecen en más películas,
    junto con su nacionalidad.
    """
    sql = """
        SELECT a.name AS actor, a.nationality AS nacionalidad, COUNT(*) AS total_peliculas
        FROM glue_datalake.movie_actors ma
        JOIN glue_datalake.actors a ON ma.actor_id = a.id
        GROUP BY a.name, a.nationality
        ORDER BY total_peliculas DESC
        LIMIT 10
    """
    try:
        return {"data": run_query(sql)}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/generos", summary="Películas por género")
def peliculas_por_genero():
    """
    Cuenta cuántas películas existen por cada género.
    """
    sql = """
        SELECT g.name AS genero, COUNT(*) AS total_peliculas
        FROM glue_datalake.movie_genres mg
        JOIN glue_datalake.genres g ON mg.genre_id = g.id
        GROUP BY g.name
        ORDER BY total_peliculas DESC
    """
    try:
        return {"data": run_query(sql)}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/directores-top", summary="Top directores con más películas")
def directores_top(
    limit: int = Query(default=10, ge=1, le=50)
):
    """
    Devuelve los directores que han dirigido más películas.
    """
    sql = f"""
        SELECT d.name AS director, COUNT(*) AS total_peliculas
        FROM glue_datalake.movie_directors md
        JOIN glue_datalake.directors d ON md.director_id = d.id
        GROUP BY d.name
        ORDER BY total_peliculas DESC
        LIMIT {limit}
    """
    try:
        return {"data": run_query(sql)}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))