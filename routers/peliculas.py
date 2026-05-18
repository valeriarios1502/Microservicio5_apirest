from fastapi import APIRouter, HTTPException, Query
from client import run_query

router = APIRouter()


@router.get("/top-calificadas", summary="Top 10 películas mejor calificadas")
def top_peliculas_calificadas():
    sql = """
        SELECT id, title, year, rating
        FROM glue_datalake.movies_csv
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
    sql = """
        SELECT a.name AS actor, a.nationality AS nacionalidad, COUNT(*) AS total_peliculas
        FROM glue_datalake.movie_actors_csv ma
        JOIN glue_datalake.actors_csv a ON ma.actor_id = a.id
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
    sql = """
        SELECT g.name AS genero, COUNT(*) AS total_peliculas
        FROM glue_datalake.movie_genres_csv mg
        JOIN glue_datalake.genres_csv g ON mg.genre_id = g.id
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
    sql = f"""
        SELECT d.name AS director, COUNT(*) AS total_peliculas
        FROM glue_datalake.movie_directors_csv md
        JOIN glue_datalake.directors_csv d ON md.director_id = d.id
        GROUP BY d.name
        ORDER BY total_peliculas DESC
        LIMIT {limit}
    """
    try:
        return {"data": run_query(sql)}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
