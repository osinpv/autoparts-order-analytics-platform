"""add movement type constraint

Revision ID: 3b15a7f95e4f
Revises: 28baa9411518
Create Date: 2026-04-25 18:06:44.133027

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3b15a7f95e4f'
down_revision: Union[str, Sequence[str], None] = '28baa9411518'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_check_constraint(
        "ck_inventory_movement_type_allowed",
        "inventory_movement",
        "movement_type in ('INITIAL_LOAD', 'RECEIVE', 'RESERVE', 'RELEASE', 'SHIP', 'ADJUSTMENT')",
        schema="autoparts_owner",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "ck_inventory_movement_type_allowed",
        "inventory_movement",
        schema="autoparts_owner",
        type_="check",
    )
    # ### end Alembic commands ###
