import grpc
import traceback

from app import main as api_routes
from app.database.session import SessionLocal
from app.models.movies import Movie
from app.schemas.movie import MovieBase, MovieUpdate
from app.transports.grpc.generated import movie_pb2, movie_pb2_grpc


def _to_proto_movie(movie) -> movie_pb2.Movie:
    return movie_pb2.Movie(
        id=movie.id,
        title=str(movie.title or ""),
        rating=float(movie.rating or 0.0),
        comments_count=int(movie.comments_count or 0),
        quote=str(movie.quote or ""),
        url=str(movie.url or ""),
    )


class MovieService(movie_pb2_grpc.MovieServiceServicer):
    def ListMovies(self, request, context):
        try:
            min_rating = request.min_rating if request.HasField("min_rating") else None
            max_rating = request.max_rating if request.HasField("max_rating") else None
            with SessionLocal() as db:
                try:
                    movies = api_routes.list_movies(
                        skip=max(request.skip, 0),
                        limit=request.limit if request.limit > 0 else 20,
                        min_rating=min_rating,
                        max_rating=max_rating,
                        db=db,
                    )
                except Exception as exc:
                    if "min_rating cannot exceed max_rating" in str(exc):
                        context.abort(
                            grpc.StatusCode.INVALID_ARGUMENT,
                            "min_rating cannot exceed max_rating",
                        )
                    context.abort(grpc.StatusCode.INTERNAL, f"Failed to list movies: {exc!r}")
            try:
                return movie_pb2.ListMoviesResponse(items=[_to_proto_movie(m) for m in movies])
            except Exception as exc:
                context.abort(grpc.StatusCode.INTERNAL, f"Failed to encode movies: {exc!r}")
        except Exception as exc:
            print("Unhandled ListMovies exception:\n" + traceback.format_exc())
            context.abort(grpc.StatusCode.INTERNAL, f"Unhandled ListMovies error: {type(exc).__name__}: {exc!r}")

    def GetMovie(self, request, context):
        try:
            with SessionLocal() as db:
                try:
                    movie = api_routes.get_movie(request.movie_id, db=db)
                except Exception as exc:
                    if "Movie not found" in str(exc):
                        context.abort(grpc.StatusCode.NOT_FOUND, "Movie not found")
                    context.abort(grpc.StatusCode.INTERNAL, f"Failed to get movie: {exc!r}")
            try:
                return _to_proto_movie(movie)
            except Exception as exc:
                context.abort(grpc.StatusCode.INTERNAL, f"Failed to encode movie: {exc!r}")
        except Exception as exc:
            print("Unhandled GetMovie exception:\n" + traceback.format_exc())
            context.abort(grpc.StatusCode.INTERNAL, f"Unhandled GetMovie error: {type(exc).__name__}: {exc!r}")

    def CreateMovie(self, request, context):
        try:
            with SessionLocal() as db:
                try:
                    movie_in = MovieBase(
                        title=request.title,
                        rating=request.rating,
                        comments_count=request.comments_count,
                        quote=request.quote,
                        url=request.url,
                    )
                    movie = api_routes.create_movie_api(movie_in, db=db)
                except Exception as exc:
                    if "Movie URL already exists" in str(exc):
                        context.abort(grpc.StatusCode.ALREADY_EXISTS, "Movie URL already exists")
                    context.abort(grpc.StatusCode.INTERNAL, f"Failed to create movie: {exc!r}")
            try:
                return _to_proto_movie(movie)
            except Exception as exc:
                context.abort(grpc.StatusCode.INTERNAL, f"Failed to encode movie: {exc!r}")
        except Exception as exc:
            print("Unhandled CreateMovie exception:\n" + traceback.format_exc())
            context.abort(grpc.StatusCode.INTERNAL, f"Unhandled CreateMovie error: {type(exc).__name__}: {exc!r}")

    def UpdateMovie(self, request, context):
        try:
            with SessionLocal() as db:
                try:
                    payload = {}
                    if request.HasField("title"):
                        payload["title"] = request.title
                    if request.HasField("rating"):
                        payload["rating"] = request.rating
                    if request.HasField("comments_count"):
                        payload["comments_count"] = request.comments_count
                    if request.HasField("quote"):
                        payload["quote"] = request.quote
                    if request.HasField("url"):
                        payload["url"] = request.url
                    movie_in = MovieUpdate(**payload)
                    movie = api_routes.update_movie_api(request.movie_id, movie_in, db=db)
                except Exception as exc:
                    if "Movie not found" in str(exc):
                        context.abort(grpc.StatusCode.NOT_FOUND, "Movie not found")
                    context.abort(grpc.StatusCode.INTERNAL, f"Failed to update movie: {exc!r}")
            try:
                return _to_proto_movie(movie)
            except Exception as exc:
                context.abort(grpc.StatusCode.INTERNAL, f"Failed to encode movie: {exc!r}")
        except Exception as exc:
            print("Unhandled UpdateMovie exception:\n" + traceback.format_exc())
            context.abort(grpc.StatusCode.INTERNAL, f"Unhandled UpdateMovie error: {type(exc).__name__}: {exc!r}")

    def DeleteMovie(self, request, context):
        try:
            with SessionLocal() as db:
                try:
                    result = api_routes.delete_movie_api(request.movie_id, db=db)
                except Exception as exc:
                    if "Movie not found" in str(exc):
                        context.abort(grpc.StatusCode.NOT_FOUND, "Movie not found")
                    context.abort(grpc.StatusCode.INTERNAL, f"Failed to delete movie: {exc!r}")
            return movie_pb2.DeleteMovieResponse(message=result["message"])
        except Exception as exc:
            print("Unhandled DeleteMovie exception:\n" + traceback.format_exc())
            context.abort(grpc.StatusCode.INTERNAL, f"Unhandled DeleteMovie error: {type(exc).__name__}: {exc!r}")

    def ClearMovies(self, request, context):
        try:
            with SessionLocal() as db:
                try:
                    result = api_routes.clear_movies_api(db=db)
                except Exception as exc:
                    context.abort(grpc.StatusCode.INTERNAL, f"Failed to clear movies: {exc!r}")
            return movie_pb2.ClearMoviesResponse(deleted_count=result["deleted_count"])
        except Exception as exc:
            print("Unhandled ClearMovies exception:\n" + traceback.format_exc())
            context.abort(grpc.StatusCode.INTERNAL, f"Unhandled ClearMovies error: {type(exc).__name__}: {exc!r}")
