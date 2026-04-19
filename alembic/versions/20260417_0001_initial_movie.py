"""initial schema (movie table)

Revision ID: 20260417_0001
Revises:
Create Date: 2026-04-17

This revision matches the SQLAlchemy model `Movie` (table name `movie`).
Use `alembic stamp 20260417_0001` on databases that already have this table.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260417_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "movie",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("rating", sa.Float(), nullable=True),
        sa.Column("comments_count", sa.Integer(), nullable=True),
        sa.Column("quote", sa.String(), nullable=True),
        sa.Column("url", sa.String(), nullable=True),
    )
    op.create_index(op.f("ix_movie_id"), "movie", ["id"], unique=False)
    op.create_index(op.f("ix_movie_url"), "movie", ["url"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_movie_url"), table_name="movie")
    op.drop_index(op.f("ix_movie_id"), table_name="movie")
    op.drop_table("movie")
