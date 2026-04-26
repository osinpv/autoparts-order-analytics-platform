from sqlalchemy import text

from tests.helpers import create_inventory_setup


def test_ship_inventory_more_than_reserved_fails(client, db_session):
    setup = create_inventory_setup(
        client,
        brand_name="Textar",
        sku="BRK-014",
        product_name="Ship Failure Pads",
        price="65.00",
        warehouse_code="SHIPFAIL",
        warehouse_name="Ship Failure Warehouse",
        region="Florida",
        on_hand_qty=10,
        reserved_qty=1,
    )

    balance = setup["balance"]

    ship_response = client.post(
        f"/inventory-balances/{balance['inventory_balance_id']}/ship",
        json={"qty": 2},
    )

    assert ship_response.status_code == 400
    assert ship_response.json()["detail"] == "Cannot ship more than currently reserved. Requested=2, reserved=1."

    row = db_session.execute(
        text("""
            select on_hand_qty, reserved_qty
            from autoparts_owner.inventory_balance
            where inventory_balance_id = :balance_id
        """),
        {"balance_id": balance["inventory_balance_id"]},
    ).fetchone()

    assert row is not None
    assert row[0] == 10
    assert row[1] == 1

    movement_rows = db_session.execute(
        text("""
            select movement_type, qty
            from autoparts_owner.inventory_movement
            order by inventory_movement_id
        """)
    ).fetchall()

    assert len(movement_rows) == 1
    assert movement_rows[0][0] == "INITIAL_LOAD"
    assert movement_rows[0][1] == 10
