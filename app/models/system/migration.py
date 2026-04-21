from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.util import CommandError
from sqlalchemy import inspect

from app.models.movies import Movie  # noqa: F401
from app.models.test import Test  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.system.base_class import Base
from app.models.system.session import engine

# 初始化数据结构：表完整则跳过，缺失才补建。
def init_db() -> None:
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    expected_tables = set(Base.metadata.tables.keys())
    missing_tables = sorted(expected_tables - existing_tables)

    if not missing_tables:
        print("数据库表结构正常，跳过 create_all。")
        return

    Base.metadata.create_all(bind=engine, checkfirst=True)
    print(f"检测到缺失表 {missing_tables}，已通过 metadata.create_all 补齐。")


def _alembic_config() -> Config:
    project_root = Path(__file__).resolve().parents[3]
    return Config(str(project_root / "alembic.ini"))


def _has_pending_model_changes(alembic_cfg: Config) -> bool:
    try:
        command.check(alembic_cfg)
        return False
    except CommandError as exc:
        if "New upgrade operations detected" in str(exc):
            return True
        raise


def run_startup_migrations() -> None:
    """
    Run Alembic on startup:
    1) upgrade existing revisions
    2) autogenerate a new revision if model changes exist
    3) upgrade again to apply the new revision
    """
    alembic_cfg = _alembic_config()
    command.upgrade(alembic_cfg, "head")
    if _has_pending_model_changes(alembic_cfg):
        command.revision(
            alembic_cfg,
            message="auto_startup_sync",
            autogenerate=True,
        )
        command.upgrade(alembic_cfg, "head")
