from sqlalchemy import Column, Integer

from app.models.system.base_class import Base


class Test(Base):

    id = Column(Integer, primary_key=True)
    number = Column(Integer)