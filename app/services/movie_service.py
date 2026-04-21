# 电影服务层：封装电影接口业务逻辑。

from sqlalchemy.orm import Session

from app.core.movie_crud import movie_core_crud
from app.models.movies import Movie
from app.schemas.movie import MovieListQuery


class MovieService:
    # 查询电影列表。
    def list_movies(self, db: Session, query: MovieListQuery) -> list[Movie]:
        return movie_core_crud.list_movies(
            db,
            skip=query.skip,
            limit=query.limit,
            min_rating=query.min_rating,
            max_rating=query.max_rating,
        )

    # 按ID查询电影。
    def get_movie(self, db: Session, movie_id: int) -> Movie | None:
        return movie_core_crud.get(db, movie_id)

    # 按URL查询电影。
    def get_movie_by_url(self, db: Session, url: str) -> Movie | None:
        return movie_core_crud.get_by_url(db, url)

    # 新增电影。
    def create_movie(self, db: Session, movie_data: dict) -> Movie:
        return movie_core_crud.create(db, obj_in=movie_data)

    # 更新电影。
    def update_movie(self, db: Session, movie: Movie, update_data: dict) -> Movie:
        return movie_core_crud.update(db, db_obj=movie, obj_in=update_data)

    # 删除单个电影。
    def delete_movie(self, db: Session, movie_id: int) -> Movie | None:
        return movie_core_crud.remove(db, id=movie_id)

    # 清空电影数据。
    def clear_movies(self, db: Session) -> int:
        return movie_core_crud.delete_all(db)


movie_service = MovieService()

