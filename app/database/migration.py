import os

from sqlalchemy import text

from app.database.base_class import Base
from app.database.session import engine
from app.models.movies import Movie  # noqa: F401

MIGRATIONS: list[tuple[str, str]] = [
    (
        "20260417_rename_votes_to_comments_count",
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'movie' AND column_name = 'votes'
            ) AND NOT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'movie' AND column_name = 'comments_count'
            ) THEN
                ALTER TABLE movie RENAME COLUMN votes TO comments_count;
            END IF;
        END $$;
        """,
    ),
]


def _ensure_migration_table() -> None:
    create_sql = text(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id VARCHAR(255) PRIMARY KEY,
            executed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        """
    )
    with engine.begin() as conn:
        conn.execute(create_sql)


def run_migrations() -> None:
    _ensure_migration_table()
    with engine.begin() as conn:
        for migration_id, migration_sql in MIGRATIONS:
            exists = conn.execute(
                text("SELECT 1 FROM schema_migrations WHERE id = :id"),
                {"id": migration_id},
            ).scalar()
            if exists:
                continue
            conn.execute(text(migration_sql))
            conn.execute(
                text("INSERT INTO schema_migrations (id) VALUES (:id)"),
                {"id": migration_id},
            )


def init_db() -> None:
    alembic_flag = os.getenv("RUN_ALEMBIC_UPGRADE", "").strip().lower()
    alembic_enabled = alembic_flag in {"1", "true", "yes", "on"}
    if not alembic_enabled:
        Base.metadata.create_all(bind=engine)
    run_migrations()
    if alembic_enabled:
        print("数据库迁移：已跳过 SQLAlchemy create_all（由 Alembic 管理表结构）。")
    else:
        print("数据库表已创建（基于 Movie 模型）。")
