from sqlalchemy import text

from tests.helpers import create_order_setup, release_order, reserve_order


def test_ship_order_after_release_fails(client, db_session):
    setup = create_order_setup(
        client,
        sku="BRK-011",
        product_name="Ship After Release Pads",
        price="91.99",
        warehouse_code="SHIPREL",
        warehouse_name="Ship After Release Warehouse",
        region="Florida",
        on_hand_qty=10,
        reserved_qty=0,
        order_number="SO-400004",
        customer_email="john@example.com",
        order_qty=2,
    )

    balance = setup["balance"]
    order = setup["order"]

    reserve_response = reserve_order(client, order["order_id"])
    assert reserve_response["order_status"] == "RESERVED"

    release_response = release_order(client, order["order_id"])
    assert release_response["order_status"] == "RELEASED"

    ship_response = client.post(f"/orders/{order['order_id']}/ship")
    assert ship_response.status_code == 400
    assert ship_response.json()["detail"] == "Only orders in RESERVED status can be shipped."

    order_row = db_session.execute(
        text("""
            select order_status
            from autoparts_owner.sales_order
            where order_id = :order_id
        """),
        {"order_id": order["order_id"]},
    ).fetchone()
    assert order_row is not None
    assert order_row[0] == "RELEASED"

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
    assert len(movement_rows) == 3
    assert [row[0] for row in movement_rows] == ["INITIAL_LOAD", "RESERVE", "RELEASE"]
