from sqlalchemy import text

from tests.helpers import create_and_complete_payment, create_order_setup, reserve_order, ship_order


def test_return_order_twice_fails(client, db_session):
    setup = create_order_setup(
        client,
        sku="BRK-022",
        product_name="Return Twice Pads",
        price="97.99",
        warehouse_code="RET2",
        warehouse_name="Return Twice Warehouse",
        region="Florida",
        on_hand_qty=10,
        reserved_qty=0,
        order_number="SO-700003",
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

    first_return_response = client.post(f"/orders/{order['order_id']}/return")
    assert first_return_response.status_code == 200
    assert first_return_response.json()["order_status"] == "RETURNED"

    second_return_response = client.post(f"/orders/{order['order_id']}/return")
    assert second_return_response.status_code == 400
    assert second_return_response.json()["detail"] == "Order is already returned."

    order_row = db_session.execute(
        text("""
            select order_status
            from autoparts_owner.sales_order
            where order_id = :order_id
        """),
        {"order_id": order["order_id"]},
    ).fetchone()

    assert order_row is not None
    assert order_row[0] == "RETURNED"

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

    movement_rows = db_session.execute(
        text("""
            select movement_type
            from autoparts_owner.inventory_movement
            order by inventory_movement_id
        """)
    ).fetchall()

    assert len(movement_rows) == 4
    assert [row[0] for row in movement_rows] == ["INITIAL_LOAD", "RESERVE", "SHIP", "RETURN"]
