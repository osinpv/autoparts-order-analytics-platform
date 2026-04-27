from sqlalchemy import text

from tests.helpers import create_and_complete_payment, create_order_setup, reserve_order, ship_order


def test_return_shipped_order_success(client, db_session):
    setup = create_order_setup(
        client,
        sku="BRK-020",
        product_name="Return Shipped Pads",
        price="94.99",
        warehouse_code="RETOK",
        warehouse_name="Return Success Warehouse",
        region="Florida",
        on_hand_qty=10,
        reserved_qty=0,
        order_number="SO-700001",
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

    return_response = client.post(f"/orders/{order['order_id']}/return")
    assert return_response.status_code == 200

    payload = return_response.json()
    assert payload["order_id"] == order["order_id"]
    assert payload["order_status"] == "RETURNED"

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

    movement_rows = db_session.execute(
        text("""
            select movement_type, qty, reference_type, resulting_on_hand_qty, resulting_reserved_qty
            from autoparts_owner.inventory_movement
            order by inventory_movement_id
        """)
    ).fetchall()

    assert len(movement_rows) == 4

    assert movement_rows[0][0] == "INITIAL_LOAD"
    assert movement_rows[0][1] == 10
    assert movement_rows[0][2] == "INVENTORY_BALANCE"
    assert movement_rows[0][3] == 10
    assert movement_rows[0][4] == 0

    assert movement_rows[1][0] == "RESERVE"
    assert movement_rows[1][1] == 2
    assert movement_rows[1][2] == "ORDER_ITEM"
    assert movement_rows[1][3] == 10
    assert movement_rows[1][4] == 2

    assert movement_rows[2][0] == "SHIP"
    assert movement_rows[2][1] == 2
    assert movement_rows[2][2] == "ORDER_ITEM"
    assert movement_rows[2][3] == 8
    assert movement_rows[2][4] == 0

    assert movement_rows[3][0] == "RETURN"
    assert movement_rows[3][1] == 2
    assert movement_rows[3][2] == "ORDER_ITEM"
    assert movement_rows[3][3] == 10
    assert movement_rows[3][4] == 0
