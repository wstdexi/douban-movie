from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.settings import settings

# 创建数据库引擎与会话工厂。
engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
