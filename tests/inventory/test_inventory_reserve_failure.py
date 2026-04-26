from sqlalchemy import text

from tests.helpers import create_inventory_setup


def test_reserve_inventory_insufficient_available(client, db_session):
    setup = create_inventory_setup(
        client,
        sku="BRK-002",
        product_name="Rear Brake Pads",
        price="59.99",
        warehouse_code="MIA",
        warehouse_name="Miami Warehouse",
        region="Florida South",
        on_hand_qty=10,
        reserved_qty=8,
    )

    balance = setup["balance"]

    reserve_response = client.post(
        f"/inventory-balances/{balance['inventory_balance_id']}/reserve",
        json={"qty": 3},
    )

    assert reserve_response.status_code == 400
    assert reserve_response.json()["detail"] == "Not enough available inventory. Requested=3, available=2."

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

    rows = db_session.execute(
        text("""
            select movement_type, qty
            from autoparts_owner.inventory_movement
            order by inventory_movement_id
        """)
    ).fetchall()

    assert len(rows) == 1
    assert rows[0][0] == "INITIAL_LOAD"
    assert rows[0][1] == 10
