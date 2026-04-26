from sqlalchemy import text

from tests.helpers import create_order_setup


def test_reserve_order_insufficient_inventory(client, db_session):
    setup = create_order_setup(
        client,
        sku="BRK-005",
        product_name="Street Brake Pads",
        price="49.99",
        warehouse_code="TAL",
        warehouse_name="Tallahassee Warehouse",
        region="Florida North",
        on_hand_qty=10,
        reserved_qty=8,
        order_number="SO-300002",
        customer_email="john@example.com",
        order_qty=3,
    )

    balance = setup["balance"]
    order = setup["order"]

    reserve_response = client.post(f"/orders/{order['order_id']}/reserve")

    assert reserve_response.status_code == 400
    assert reserve_response.json()["detail"] == (
        "Not enough available inventory. Requested=3, available=2."
    )

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
    assert balance_row[1] == 8

    movement_rows = db_session.execute(
        text("""
            select movement_type, qty, reference_type
            from autoparts_owner.inventory_movement
            order by inventory_movement_id
        """)
    ).fetchall()

    assert len(movement_rows) == 1
    assert movement_rows[0][0] == "INITIAL_LOAD"
    assert movement_rows[0][1] == 10
    assert movement_rows[0][2] == "INVENTORY_BALANCE"
