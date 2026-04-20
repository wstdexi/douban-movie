from sqlalchemy import Column, Integer, String, Boolean

from app.models.system.base_class import Base


# 用户类---继承基本类
class User(Base):

    id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    hashed_password = Column(String(100), nullable=False)
    is_superuser = Column(Boolean, nullable=False, default=False)
    signature = Column(String(100))