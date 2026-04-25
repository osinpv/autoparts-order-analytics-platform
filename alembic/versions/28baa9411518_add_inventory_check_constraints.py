"""add inventory check constraints

Revision ID: 28baa9411518
Revises: 308429d23eb7
Create Date: 2026-04-25 17:58:01.079403

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '28baa9411518'
down_revision: Union[str, Sequence[str], None] = '308429d23eb7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_check_constraint(
        "ck_inventory_balance_on_hand_nonnegative",
        "inventory_balance",
        "on_hand_qty >= 0",
        schema="autoparts_owner",
    )
    op.create_check_constraint(
        "ck_inventory_balance_reserved_nonnegative",
        "inventory_balance",
        "reserved_qty >= 0",
        schema="autoparts_owner",
    )
    op.create_check_constraint(
        "ck_inventory_balance_reserved_not_gt_on_hand",
        "inventory_balance",
        "reserved_qty <= on_hand_qty",
        schema="autoparts_owner",
    )

    op.create_check_constraint(
        "ck_inventory_movement_qty_positive",
        "inventory_movement",
        "qty > 0",
        schema="autoparts_owner",
    )
    op.create_check_constraint(
        "ck_inventory_movement_resulting_on_hand_nonnegative",
        "inventory_movement",
        "resulting_on_hand_qty >= 0",
        schema="autoparts_owner",
    )
    op.create_check_constraint(
        "ck_inventory_movement_resulting_reserved_nonnegative",
        "inventory_movement",
        "resulting_reserved_qty >= 0",
        schema="autoparts_owner",
    )
    op.create_check_constraint(
        "ck_inventory_movement_resulting_reserved_not_gt_on_hand",
        "inventory_movement",
        "resulting_reserved_qty <= resulting_on_hand_qty",
        schema="autoparts_owner",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "ck_inventory_movement_resulting_reserved_not_gt_on_hand",
        "inventory_movement",
        schema="autoparts_owner",
        type_="check",
    )
    op.drop_constraint(
        "ck_inventory_movement_resulting_reserved_nonnegative",
        "inventory_movement",
        schema="autoparts_owner",
        type_="check",
    )
    op.drop_constraint(
        "ck_inventory_movement_resulting_on_hand_nonnegative",
        "inventory_movement",
        schema="autoparts_owner",
        type_="check",
    )
    op.drop_constraint(
        "ck_inventory_movement_qty_positive",
        "inventory_movement",
        schema="autoparts_owner",
        type_="check",
    )

    op.drop_constraint(
        "ck_inventory_balance_reserved_not_gt_on_hand",
        "inventory_balance",
        schema="autoparts_owner",
        type_="check",
    )
    op.drop_constraint(
        "ck_inventory_balance_reserved_nonnegative",
        "inventory_balance",
        schema="autoparts_owner",
        type_="check",
    )
    op.drop_constraint(
        "ck_inventory_balance_on_hand_nonnegative",
        "inventory_balance",
        schema="autoparts_owner",
        type_="check",
    )
    # ### end Alembic commands ###
