"""allow cancelled sales order status

Revision ID: 040883958b18
Revises: e2fee5df1534
Create Date: 2026-04-26 15:38:06.097741

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '040883958b18'
down_revision: Union[str, Sequence[str], None] = 'e2fee5df1534'
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
        "order_status in ('NEW', 'RESERVED', 'RELEASED', 'SHIPPED', 'CANCELLED')",
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
        "order_status in ('NEW', 'RESERVED', 'RELEASED', 'SHIPPED')",
        schema="autoparts_owner",
    )
