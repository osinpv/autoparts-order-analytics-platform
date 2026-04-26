"""add sales order status constraint

Revision ID: e2fee5df1534
Revises: ec7a3715a5b6
Create Date: 2026-04-26 13:48:27.372808

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e2fee5df1534'
down_revision: Union[str, Sequence[str], None] = 'ec7a3715a5b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_check_constraint(
        "ck_sales_order_status_allowed",
        "sales_order",
        "order_status in ('NEW', 'RESERVED', 'RELEASED', 'SHIPPED')",
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
