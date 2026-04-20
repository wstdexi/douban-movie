from typing import Generator

from sqlalchemy.orm import Session

from app.models.system.session import SessionLocal


# 提供数据库会话依赖，供路由层注入使用。
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()