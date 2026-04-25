"""add reference type constraint

Revision ID: 8d15d6f48730
Revises: 3b15a7f95e4f
Create Date: 2026-04-25 18:12:52.626093

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8d15d6f48730'
down_revision: Union[str, Sequence[str], None] = '3b15a7f95e4f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_check_constraint(
        "ck_inventory_movement_reference_type_allowed",
        "inventory_movement",
        "reference_type is null or reference_type in ('INVENTORY_BALANCE', 'MANUAL', 'ORDER', 'ORDER_ITEM', 'SHIPMENT')",
        schema="autoparts_owner",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "ck_inventory_movement_reference_type_allowed",
        "inventory_movement",
        schema="autoparts_owner",
        type_="check",
    )
    # ### end Alembic commands ###
