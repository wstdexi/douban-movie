from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.movies import Movie
from app.schemas.movie import MovieBase, MovieUpdate


def get_all_movies(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    min_rating: float | None = None,
    max_rating: float | None = None,
) -> list[Movie]:
    stmt = select(Movie)
    if min_rating is not None:
        stmt = stmt.where(Movie.rating >= min_rating)
    if max_rating is not None:
        stmt = stmt.where(Movie.rating <= max_rating)

    stmt = stmt.order_by(Movie.rating.desc(), Movie.comments_count.desc(), Movie.id.asc())
    stmt = stmt.offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


def get_movie_by_id(db: Session, movie_id: int) -> Movie | None:
    stmt = select(Movie).where(Movie.id == movie_id)
    return db.scalar(stmt)


def get_movie_by_url(db: Session, url: str) -> Movie | None:
    stmt = select(Movie).where(Movie.url == url)
    return db.scalar(stmt)


def create_movie(db: Session, movie_in: MovieBase) -> Movie:
    movie_data = movie_in.model_dump()
    movie_data["url"] = str(movie_data["url"])
    movie = Movie(**movie_data)
    db.add(movie)
    db.commit()
    db.refresh(movie)
    return movie


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


def delete_movie(db: Session, movie: Movie) -> None:
    db.delete(movie)
    db.commit()


def delete_all_movies(db: Session) -> int:
    result = db.execute(delete(Movie))
    db.commit()
    return result.rowcount or 0
