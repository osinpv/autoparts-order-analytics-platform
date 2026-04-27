from sqlalchemy import text

from tests.helpers import create_order_setup


def test_return_new_order_fails(client, db_session):
    setup = create_order_setup(
        client,
        sku="BRK-021",
        product_name="Return New Pads",
        price="78.99",
        warehouse_code="RETNEW",
        warehouse_name="Return New Warehouse",
        region="Florida",
        on_hand_qty=10,
        reserved_qty=0,
        order_number="SO-700002",
        customer_email="john@example.com",
        order_qty=2,
    )

    balance = setup["balance"]
    order = setup["order"]

    return_response = client.post(f"/orders/{order['order_id']}/return")
    assert return_response.status_code == 400
    assert return_response.json()["detail"] == "Only shipped or delivered orders can be returned."

    # order remains NEW
    order_row = db_session.execute(
        text("""
            select order_status
            from autoparts_owner.sales_order
            where order_id = :order_id
        """),
        {"order_id": order["order_id"]},
    ).fetchone()

    assert order_row is not None
    assert order_row[0] == "NEW"

    # inventory unchanged
    balance_row = db_session.execute(
        text("""
            select on_hand_qty, reserved_qty
            from autoparts_owner.inventory_balance
            where inventory_balance_id = :balance_id
        """),
        {"balance_id": balance["inventory_balance_id"]},
    ).fetchone()

    assert balance_row is not None
    assert balance_row[0] == 10
    assert balance_row[1] == 0

    # no extra ledger row beyond INITIAL_LOAD
    movement_rows = db_session.execute(
        text("""
            select movement_type
            from autoparts_owner.inventory_movement
            order by inventory_movement_id
        """)
    ).fetchall()

    assert len(movement_rows) == 1
    assert movement_rows[0][0] == "INITIAL_LOAD"
