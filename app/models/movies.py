from sqlalchemy import Column, Float, Integer, String

from app.database.base_class import Base


class Movie(Base):

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    rating = Column(Float)
    comments_count = Column(Integer)
    quote = Column(String)
    url = Column(String, unique=True, index=True)
