"""move alembic_version to autoparts_owner

Revision ID: 0fff851f62fd
Revises: 23576ce5a079
Create Date: 2026-04-24 17:11:39.449106

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0fff851f62fd'
down_revision: Union[str, Sequence[str], None] = '23576ce5a079'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS autoparts_owner")
    op.execute("ALTER TABLE public.alembic_version SET SCHEMA autoparts_owner")


def downgrade() -> None:
    op.execute("ALTER TABLE autoparts_owner.alembic_version SET SCHEMA public")
