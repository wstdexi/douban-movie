import os

import grpc

from app.transports.grpc.generated import movie_pb2, movie_pb2_grpc


# gRPC客户端封装，提供电影相关远程调用方法。
class MovieClient:
    def __init__(self, target: str | None = None) -> None:
        target = target or os.getenv("GRPC_TARGET", "127.0.0.1:50051")
        self.channel = grpc.insecure_channel(target)
        self.stub = movie_pb2_grpc.MovieServiceStub(self.channel)

    def list_movies(
        self,
        skip: int = 0,
        limit: int = 20,
        min_rating: float | None = None,
        max_rating: float | None = None,
    ) -> list[movie_pb2.Movie]:
        request = movie_pb2.ListMoviesRequest(skip=skip, limit=limit)
        if min_rating is not None:
            request.min_rating = min_rating
        if max_rating is not None:
            request.max_rating = max_rating
        response = self.stub.ListMovies(request)
        return list(response.items)

    def create_movie(
        self,
        title: str,
        rating: float,
        comments_count: int,
        quote: str,
        url: str,
    ) -> movie_pb2.Movie:
        request = movie_pb2.CreateMovieRequest(
            title=title,
            rating=rating,
            comments_count=comments_count,
            quote=quote,
            url=url,
        )
        return self.stub.CreateMovie(request)

    def get_movie(self, movie_id: int) -> movie_pb2.Movie:
        request = movie_pb2.GetMovieRequest(movie_id=movie_id)
        return self.stub.GetMovie(request)

    def update_movie(
        self,
        movie_id: int,
        title: str | None = None,
        rating: float | None = None,
        comments_count: int | None = None,
        quote: str | None = None,
        url: str | None = None,
    ) -> movie_pb2.Movie:
        request = movie_pb2.UpdateMovieRequest(movie_id=movie_id)
        if title is not None:
            request.title = title
        if rating is not None:
            request.rating = rating
        if comments_count is not None:
            request.comments_count = comments_count
        if quote is not None:
            request.quote = quote
        if url is not None:
            request.url = url
        return self.stub.UpdateMovie(request)

    def delete_movie(self, movie_id: int) -> movie_pb2.DeleteMovieResponse:
        request = movie_pb2.DeleteMovieRequest(movie_id=movie_id)
        return self.stub.DeleteMovie(request)

    def clear_movies(self) -> movie_pb2.ClearMoviesResponse:
        request = movie_pb2.ClearMoviesRequest()
        return self.stub.ClearMovies(request)

    def close(self) -> None:
        self.channel.close()
