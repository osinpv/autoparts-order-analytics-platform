"""allow delivered sales order status

Revision ID: dd184798b75f
Revises: 21066c83b6b2
Create Date: 2026-04-26 17:47:33.540545

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dd184798b75f'
down_revision: Union[str, Sequence[str], None] = '21066c83b6b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint(
        "ck_sales_order_status_allowed",
        "sales_order",
        schema="autoparts_owner",
        type_="check",
    )
    op.create_check_constraint(
        "ck_sales_order_status_allowed",
        "sales_order",
        "order_status in ('NEW', 'RESERVED', 'RELEASED', 'SHIPPED', 'CANCELLED', 'RETURNED', 'DELIVERED')",
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
        "order_status in ('NEW', 'RESERVED', 'RELEASED', 'SHIPPED', 'CANCELLED', 'RETURNED')",
        schema="autoparts_owner",
    )