import csv
from io import StringIO

import grpc
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse

from app.transports.grpc.clients.movie_client import MovieClient

app = FastAPI(title="Douban gRPC Gateway", version="1.0.0")


def _to_http_error(exc: grpc.RpcError) -> HTTPException:
    code = exc.code()
    detail = exc.details() or "gRPC call failed"
    if code == grpc.StatusCode.NOT_FOUND:
        return HTTPException(status_code=404, detail=detail)
    if code == grpc.StatusCode.ALREADY_EXISTS:
        return HTTPException(status_code=409, detail=detail)
    if code == grpc.StatusCode.INVALID_ARGUMENT:
        return HTTPException(status_code=400, detail=detail)
    return HTTPException(status_code=500, detail=detail)


def _movie_to_dict(movie) -> dict:
    return {
        "id": movie.id,
        "title": movie.title,
        "rating": movie.rating,
        "comments_count": movie.comments_count,
        "quote": movie.quote,
        "url": movie.url,
    }


@app.get("/v1/movies")
def list_movies(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    min_rating: float | None = Query(default=None, ge=0, le=10),
    max_rating: float | None = Query(default=None, ge=0, le=10),
):
    client = MovieClient()
    try:
        movies = client.list_movies(
            skip=skip,
            limit=limit,
            min_rating=min_rating,
            max_rating=max_rating,
        )
        return [_movie_to_dict(movie) for movie in movies]
    except grpc.RpcError as exc:
        raise _to_http_error(exc) from exc
    finally:
        client.close()


@app.get("/v1/movies/{movie_id}")
def get_movie(movie_id: int):
    client = MovieClient()
    try:
        movie = client.get_movie(movie_id)
        return _movie_to_dict(movie)
    except grpc.RpcError as exc:
        raise _to_http_error(exc) from exc
    finally:
        client.close()


@app.post("/v1/movies")
def create_movie(payload: dict):
    client = MovieClient()
    try:
        movie = client.create_movie(
            title=payload["title"],
            rating=float(payload["rating"]),
            comments_count=int(payload["comments_count"]),
            quote=payload.get("quote", ""),
            url=payload["url"],
        )
        return _movie_to_dict(movie)
    except KeyError as exc:
        raise HTTPException(status_code=400, detail=f"Missing field: {exc}") from exc
    except grpc.RpcError as exc:
        raise _to_http_error(exc) from exc
    finally:
        client.close()


@app.put("/v1/movies/{movie_id}")
def update_movie(movie_id: int, payload: dict):
    client = MovieClient()
    try:
        movie = client.update_movie(
            movie_id=movie_id,
            title=payload.get("title"),
            rating=payload.get("rating"),
            comments_count=payload.get("comments_count"),
            quote=payload.get("quote"),
            url=payload.get("url"),
        )
        return _movie_to_dict(movie)
    except grpc.RpcError as exc:
        raise _to_http_error(exc) from exc
    finally:
        client.close()


@app.delete("/v1/movies/{movie_id}")
def delete_movie(movie_id: int):
    client = MovieClient()
    try:
        response = client.delete_movie(movie_id)
        return {"message": response.message}
    except grpc.RpcError as exc:
        raise _to_http_error(exc) from exc
    finally:
        client.close()


@app.delete("/v1/movies")
def clear_movies():
    client = MovieClient()
    try:
        response = client.clear_movies()
        return {"deleted_count": response.deleted_count}
    except grpc.RpcError as exc:
        raise _to_http_error(exc) from exc
    finally:
        client.close()


@app.get("/v1/movies/export/csv")
def export_movies_csv(
    min_rating: float | None = Query(default=None, ge=0, le=10),
    max_rating: float | None = Query(default=None, ge=0, le=10),
):
    client = MovieClient()
    try:
        movies = client.list_movies(
            skip=0,
            limit=10000,
            min_rating=min_rating,
            max_rating=max_rating,
        )
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["title", "rating", "comments_count", "quote", "url"])
        for movie in movies:
            writer.writerow(
                [movie.title, movie.rating, movie.comments_count, movie.quote, movie.url]
            )
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": 'attachment; filename="movies.csv"'},
        )
    except grpc.RpcError as exc:
        raise _to_http_error(exc) from exc
    finally:
        client.close()
