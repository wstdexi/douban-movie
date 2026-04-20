from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.movies import Movie
from app.schemas.movie import MovieBase, MovieUpdate


# 用于获取所有电影列表
def get_all_movies(
    db: Session,
    *,
    skip: int,
    limit: int,
    min_rating: float | None,
    max_rating: float | None,
) -> list[Movie]:
    stmt = select(Movie)
    if min_rating is not None:
        stmt = stmt.where(Movie.rating >= min_rating)
    if max_rating is not None:
        stmt = stmt.where(Movie.rating <= max_rating)

    stmt = stmt.order_by(Movie.rating.desc(), Movie.comments_count.desc(), Movie.id.asc())
    stmt = stmt.offset(skip).limit(limit)
    return list(db.scalars(stmt).all())

# 通过ID查询电影
def get_movie_by_id(db: Session, movie_id: int) -> Movie | None:
    stmt = select(Movie).where(Movie.id == movie_id)
    return db.scalar(stmt)

#通过url查询电影
def get_movie_by_url(db: Session, url: str) -> Movie | None:
    stmt = select(Movie).where(Movie.url == url)
    return db.scalar(stmt)


# 创建电影
def create_movie(db: Session, movie_in: MovieBase) -> Movie:
    movie_data = movie_in.model_dump()
    movie_data["url"] = str(movie_data["url"])
    movie = Movie(**movie_data)
    db.add(movie)
    db.commit()
    db.refresh(movie)
    return movie


# 更新电影
def update_movie(db: Session, movie_id: int, movie_in: MovieUpdate) -> Movie:
    update_data = movie_in.model_dump(exclude_unset=True)
    if "url" in update_data and update_data["url"] is not None:
        update_data["url"] = str(update_data["url"])
    movie = get_movie_by_id(db, movie_id)
    if movie is None:
        raise ValueError("Movie not found")
    for field, value in update_data.items():
        setattr(movie, field, value)

    db.add(movie)
    db.commit()
    db.refresh(movie)
    return movie


# 删除单个电影
def delete_movie(db: Session, movie: Movie) -> None:
    db.delete(movie)
    db.commit()


# 删除所有电影
def delete_all_movies(db: Session) -> int:
    result = db.execute(delete(Movie))
    db.commit()
    return result.rowcount or 0
