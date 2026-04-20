"""add user table

Revision ID: ace8b55db2fc
Revises: 20260417_0001
Create Date: 2026-04-20 20:24:12.018952

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'ace8b55db2fc'
down_revision: Union[str, Sequence[str], None] = '20260417_0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=100), nullable=False),
        sa.Column("hashed_password", sa.String(length=100), nullable=False),
        sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("signature", sa.String(length=100), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("user")

