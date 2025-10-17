"""add is_super_admin to admin table

Revision ID: 89022f1cb3df
Revises: 0c1406fbafcb
Create Date: 2025-10-16 11:56:49.541138

"""

from typing import Optional, Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "89022f1cb3df"
down_revision: Optional[str] = "0c1406fbafcb"
branch_labels: Optional[Sequence[str]] = None
depends_on: Optional[Sequence[str]] = None


def upgrade() -> None:
    op.add_column(
        "admin",
        sa.Column("is_super_admin", sa.Boolean(), server_default="false", nullable=False),
        schema="users",
    )
    op.alter_column(
        "admin",
        "user_id",
        existing_type=sa.BIGINT(),
        type_=sa.Integer(),
        existing_nullable=False,
        autoincrement=True,
        schema="users",
    )
    op.alter_column(
        "user",
        "user_id",
        existing_type=sa.BIGINT(),
        type_=sa.Integer(),
        existing_nullable=False,
        autoincrement=True,
        schema="users",
    )


def downgrade() -> None:
    op.alter_column(
        "user",
        "user_id",
        existing_type=sa.Integer(),
        type_=sa.BIGINT(),
        existing_nullable=False,
        autoincrement=True,
        schema="users",
    )
    op.alter_column(
        "admin",
        "user_id",
        existing_type=sa.Integer(),
        type_=sa.BIGINT(),
        existing_nullable=False,
        autoincrement=True,
        schema="users",
    )
    op.drop_column("admin", "is_super_admin", schema="users")
