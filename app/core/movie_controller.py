# 电影核心控制器：继承CRUDBase，封装电影相关数据库操作。

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.core.crud import CRUDBase
from app.models.movies import Movie
from app.schemas.movie import MovieBase, MovieListQuery, MovieUpdate


class MovieCoreController(CRUDBase[Movie, MovieBase, MovieUpdate]):
    def __init__(self) -> None:
        super().__init__(Movie)

    # 分页查询电影列表（可按评分区间过滤）。
    def list_movies(self, db: Session, query: MovieListQuery) -> list[Movie]:
        stmt = select(Movie)
        if query.min_rating is not None:
            stmt = stmt.where(Movie.rating >= query.min_rating)
        if query.max_rating is not None:
            stmt = stmt.where(Movie.rating <= query.max_rating)
        stmt = stmt.order_by(Movie.rating.desc(), Movie.comments_count.desc(), Movie.id.asc())
        stmt = stmt.offset(query.skip).limit(query.limit)
        return list(db.scalars(stmt).all())

    # 通过URL查询电影。
    def get_by_url(self, db: Session, url: str) -> Movie | None:
        stmt = select(Movie).where(Movie.url == url)
        return db.scalar(stmt)

    # 清空电影表。
    def delete_all(self, db: Session) -> int:
        result = db.execute(delete(Movie))
        db.commit()
        return result.rowcount or 0

    # 统计电影数量。
    def count(self, db: Session) -> int:
        stmt = select(func.count()).select_from(Movie)
        return int(db.scalar(stmt) or 0)


movie_core_controller = MovieCoreController()

