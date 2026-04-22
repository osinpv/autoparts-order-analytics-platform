"""create autoparts_owner schema and move product

Revision ID: 3f94c0ba42cc
Revises: 709906f7d95c
Create Date: 2026-04-21 23:18:20.503710

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3f94c0ba42cc'
down_revision: Union[str, Sequence[str], None] = '709906f7d95c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS autoparts_owner")
    op.execute("ALTER TABLE public.product SET SCHEMA autoparts_owner")


def downgrade() -> None:
    op.execute("ALTER TABLE autoparts_owner.product SET SCHEMA public")
    op.execute("DROP SCHEMA IF EXISTS autoparts_owner")
