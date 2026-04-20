import csv
from io import StringIO

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.controllers.movie_controller import movie_request_controller
from app.schemas.movie import MovieBase, MovieListQuery, OutMovie, MovieUpdate
from app.services.movie_service import movie_service


# 电影路由统一归类到 OpenAPI 的 movies 标签下。
router = APIRouter(
    tags=["movies"],
    dependencies=[Depends(get_current_user)],
)


# 用于获取分页电影列表。
@router.get("/movies", response_model=list[OutMovie], summary="分页查询电影")
def list_movies(
    query: MovieListQuery = Depends(),
    db: Session = Depends(get_db),
) -> list[OutMovie]:
    try:
        movie_request_controller.validate_list_query(query)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    movies = movie_service.list_movies(db, query)
    return [OutMovie.model_validate(movie) for movie in movies]


# 通过 ID 查询单个电影。
@router.get("/movies/{movie_id}", response_model=OutMovie, summary="按ID查询电影")
def get_movie(movie_id: int, db: Session = Depends(get_db)) -> OutMovie:
    movie = movie_service.get_movie(db, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return OutMovie.model_validate(movie)


# 新增电影数据。
@router.post("/movies", response_model=OutMovie, status_code=201, summary="新增电影")
def create_movie_api(movie_in: MovieBase, db: Session = Depends(get_db)) -> OutMovie:
    existing = movie_service.get_movie_by_url(db, str(movie_in.url))
    if existing:
        raise HTTPException(status_code=409, detail="Movie URL already exists")
    movie_data = movie_request_controller.normalize_create_payload(movie_in)
    movie = movie_service.create_movie(db, movie_data)
    return OutMovie.model_validate(movie)


# 更新指定电影。
@router.put("/movies/{movie_id}", response_model=OutMovie, summary="更新电影")
def update_movie_api(
    movie_id: int,
    movie_in: MovieUpdate,
    db: Session = Depends(get_db),
) -> OutMovie:
    movie = movie_service.get_movie(db, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    update_data = movie_request_controller.normalize_update_payload(movie_in)
    updated = movie_service.update_movie(db, movie, update_data)
    return OutMovie.model_validate(updated)


# 删除单个电影。
@router.delete("/movies/{movie_id}", summary="删除电影")
def delete_movie_api(movie_id: int, db: Session = Depends(get_db)) -> dict[str, str]:
    movie = movie_service.get_movie(db, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    movie_service.delete_movie(db, movie_id)
    return {"message": "Movie deleted"}


# 清空电影表数据。
@router.delete("/movies", summary="清空电影表")
def clear_movies_api(db: Session = Depends(get_db)) -> dict[str, int]:
    deleted_count = movie_service.clear_movies(db)
    return {"deleted_count": deleted_count}


# 导出电影 CSV 文件。
@router.get("/movies/export/csv", summary="导出电影CSV")
def export_movies_csv(
    min_rating: float | None = Query(default=None, ge=0, le=10),
    max_rating: float | None = Query(default=None, ge=0, le=10),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    if min_rating is not None and max_rating is not None and min_rating > max_rating:
        raise HTTPException(status_code=400, detail="min_rating cannot exceed max_rating")

    export_query = MovieListQuery(
        skip=0,
        limit=10000,
        min_rating=min_rating,
        max_rating=max_rating,
    )
    movies = movie_service.list_movies(db, export_query)
    out_movies = [OutMovie.model_validate(movie) for movie in movies]

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["title", "rating", "comments_count", "quote", "url"])
    for movie in out_movies:
        writer.writerow(
            [
                movie.title,
                movie.rating,
                movie.comments_count,
                movie.quote,
                str(movie.url),
            ]
        )
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="movies.csv"'},
    )
