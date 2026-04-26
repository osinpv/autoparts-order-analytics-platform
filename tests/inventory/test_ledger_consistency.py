from sqlalchemy import text

from tests.helpers import create_inventory_setup


def test_ledger_sequence_for_reserve_release_ship(client, db_session):
    setup = create_inventory_setup(
        client,
        brand_name="Zimmermann",
        sku="BRK-015",
        product_name="Ledger Consistency Pads",
        price="88.00",
        warehouse_code="LEDGER1",
        warehouse_name="Ledger Warehouse",
        region="Florida",
        on_hand_qty=12,
        reserved_qty=0,
    )

    balance = setup["balance"]

    reserve_response = client.post(
        f"/inventory-balances/{balance['inventory_balance_id']}/reserve",
        json={"qty": 3},
    )
    assert reserve_response.status_code == 200

    release_response = client.post(
        f"/inventory-balances/{balance['inventory_balance_id']}/release",
        json={"qty": 1},
    )
    assert release_response.status_code == 200

    ship_response = client.post(
        f"/inventory-balances/{balance['inventory_balance_id']}/ship",
        json={"qty": 2},
    )
    assert ship_response.status_code == 200

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
            select movement_type, qty, resulting_on_hand_qty, resulting_reserved_qty
            from autoparts_owner.inventory_movement
            order by inventory_movement_id
        """)
    ).fetchall()

    assert len(movement_rows) == 4
    assert movement_rows[0] == ("INITIAL_LOAD", 12, 12, 0)
    assert movement_rows[1] == ("RESERVE", 3, 12, 3)
    assert movement_rows[2] == ("RELEASE", 1, 12, 2)
    assert movement_rows[3] == ("SHIP", 2, 10, 0)
