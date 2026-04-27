"""allow return movement and returned order status

Revision ID: 2990cfb7649b
Revises: 040883958b18
Create Date: 2026-04-26 16:50:20.279492

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2990cfb7649b'
down_revision: Union[str, Sequence[str], None] = '040883958b18'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint(
        "ck_inventory_movement_type_allowed",
        "inventory_movement",
        schema="autoparts_owner",
        type_="check",
    )
    op.create_check_constraint(
        "ck_inventory_movement_type_allowed",
        "inventory_movement",
        "movement_type in ('INITIAL_LOAD', 'RECEIVE', 'RESERVE', 'RELEASE', 'SHIP', 'ADJUSTMENT', 'RETURN')",
        schema="autoparts_owner",
    )

    op.drop_constraint(
        "ck_sales_order_status_allowed",
        "sales_order",
        schema="autoparts_owner",
        type_="check",
    )
    op.create_check_constraint(
        "ck_sales_order_status_allowed",
        "sales_order",
        "order_status in ('NEW', 'RESERVED', 'RELEASED', 'SHIPPED', 'CANCELLED', 'RETURNED')",
        schema="autoparts_owner",
    )

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "ck_sales_order_status_allowed",
        "sales_order",
        schema="autoparts_owner",
        type_="check",
    )
    op.create_check_constraint(
        "ck_sales_order_status_allowed",
        "sales_order",
        "order_status in ('NEW', 'RESERVED', 'RELEASED', 'SHIPPED', 'CANCELLED')",
        schema="autoparts_owner",
    )

    op.drop_constraint(
        "ck_inventory_movement_type_allowed",
        "inventory_movement",
        schema="autoparts_owner",
        type_="check",
    )
    op.create_check_constraint(
        "ck_inventory_movement_type_allowed",
        "inventory_movement",
        "movement_type in ('INITIAL_LOAD', 'RECEIVE', 'RESERVE', 'RELEASE', 'SHIP', 'ADJUSTMENT')",
        schema="autoparts_owner",
    )