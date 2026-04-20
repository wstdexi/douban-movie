import os

from app.models.movies import Movie  # noqa: F401
from app.models.system.base_class import Base
from app.models.system.session import engine


def _is_alembic_enabled() -> bool:
    flag = os.getenv("RUN_ALEMBIC_UPGRADE", "").strip().lower()
    return flag in {"1", "true", "yes", "on"}


def init_db() -> None:
    alembic_enabled = _is_alembic_enabled()
    if not alembic_enabled:
        Base.metadata.create_all(bind=engine)
    if alembic_enabled:
        print("数据库迁移：已跳过 SQLAlchemy create_all（由 Alembic 管理表结构）。")
    else:
        print("数据库表已创建（基于 Movie 模型）。")
