from sqlalchemy import text

from tests.helpers import create_and_complete_payment, create_order_setup, reserve_order, ship_order


def test_cancel_shipped_order_fails(client, db_session):
    setup = create_order_setup(
        client,
        sku="BRK-019",
        product_name="Cancel Shipped Pads",
        price="92.99",
        warehouse_code="CNLSHP",
        warehouse_name="Cancel Shipped Warehouse",
        region="Florida",
        on_hand_qty=10,
        reserved_qty=0,
        order_number="SO-600003",
        customer_email="john@example.com",
        order_qty=2,
    )

    balance = setup["balance"]
    order = setup["order"]

    reserve_payload = reserve_order(client, order["order_id"])
    assert reserve_payload["order_status"] == "RESERVED"

    create_and_complete_payment(client, order["order_id"])
    ship_payload = ship_order(client, order["order_id"])
    assert ship_payload["order_status"] == "SHIPPED"

    cancel_response = client.post(f"/orders/{order['order_id']}/cancel")
    assert cancel_response.status_code == 400
    assert cancel_response.json()["detail"] == "Shipped orders cannot be cancelled."

    order_row = db_session.execute(
        text("""
            select order_status
            from autoparts_owner.sales_order
            where order_id = :order_id
        """),
        {"order_id": order["order_id"]},
    ).fetchone()

    assert order_row is not None
    assert order_row[0] == "SHIPPED"

    balance_row = db_session.execute(
        text("""
            select on_hand_qty, reserved_qty
            from autoparts_owner.inventory_balance
            where inventory_balance_id = :balance_id
        """),
        {"balance_id": balance["inventory_balance_id"]},
    ).fetchone()

    assert balance_row is not None
    assert balance_row[0] == 8
    assert balance_row[1] == 0

    movement_rows = db_session.execute(
        text("""
            select movement_type
            from autoparts_owner.inventory_movement
            order by inventory_movement_id
        """)
    ).fetchall()

    assert len(movement_rows) == 3
    assert [row[0] for row in movement_rows] == ["INITIAL_LOAD", "RESERVE", "SHIP"]
