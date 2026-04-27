from sqlalchemy import text

from tests.helpers import create_order_setup


def test_cancel_new_order_success(client, db_session):
    setup = create_order_setup(
        client,
        sku="BRK-017",
        product_name="Cancel New Pads",
        price="81.99",
        warehouse_code="CNLNEW",
        warehouse_name="Cancel New Warehouse",
        region="Florida",
        on_hand_qty=10,
        reserved_qty=0,
        order_number="SO-600001",
        customer_email="john@example.com",
        order_qty=2,
    )

    balance = setup["balance"]
    order = setup["order"]

    cancel_response = client.post(f"/orders/{order['order_id']}/cancel")
    assert cancel_response.status_code == 200

    payload = cancel_response.json()
    assert payload["order_id"] == order["order_id"]
    assert payload["order_status"] == "CANCELLED"

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
    assert order_row[0] == "CANCELLED"

    movement_rows = db_session.execute(
        text("""
            select movement_type
            from autoparts_owner.inventory_movement
            order by inventory_movement_id
        """)
    ).fetchall()

    assert len(movement_rows) == 1
    assert movement_rows[0][0] == "INITIAL_LOAD"
