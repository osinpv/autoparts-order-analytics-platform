"""create autoparts_owner schema and move product

Revision ID: 23576ce5a079
Revises: 3f94c0ba42cc
Create Date: 2026-04-21 23:22:00.908822

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '23576ce5a079'
down_revision: Union[str, Sequence[str], None] = '3f94c0ba42cc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS autoparts_owner")
    op.execute("ALTER TABLE public.product SET SCHEMA autoparts_owner")


def downgrade() -> None:
    op.execute("ALTER TABLE autoparts_owner.product SET SCHEMA public")
    op.execute("DROP SCHEMA IF EXISTS autoparts_owner")
