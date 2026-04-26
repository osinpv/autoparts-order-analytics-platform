from sqlalchemy import text

from tests.helpers import create_inventory_setup


def test_reserve_inventory_success(client, db_session):
    setup = create_inventory_setup(
        client,
        sku="BRK-001",
        product_name="Front Brake Pads",
        price="79.99",
        warehouse_code="TPA",
        warehouse_name="Tampa Warehouse",
        region="Florida West",
        on_hand_qty=10,
        reserved_qty=3,
    )

    balance = setup["balance"]

    reserve_response = client.post(
        f"/inventory-balances/{balance['inventory_balance_id']}/reserve",
        json={"qty": 2},
    )

    assert reserve_response.status_code == 200

    payload = reserve_response.json()
    assert payload["inventory_balance_id"] == balance["inventory_balance_id"]
    assert payload["on_hand_qty"] == 10
    assert payload["reserved_qty"] == 5
    assert payload["available_qty"] == 5

    rows = db_session.execute(
        text("""
            select movement_type, qty, resulting_on_hand_qty, resulting_reserved_qty, reference_type
            from autoparts_owner.inventory_movement
            order by inventory_movement_id
        """)
    ).fetchall()

    assert len(rows) == 2

    assert rows[0][0] == "INITIAL_LOAD"
    assert rows[0][1] == 10
    assert rows[0][2] == 10
    assert rows[0][3] == 3
    assert rows[0][4] == "INVENTORY_BALANCE"

    assert rows[1][0] == "RESERVE"
    assert rows[1][1] == 2
    assert rows[1][2] == 10
    assert rows[1][3] == 5
    assert rows[1][4] == "INVENTORY_BALANCE"
