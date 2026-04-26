import threading
import time

import pytest
from sqlalchemy import create_engine, text

from tests.helpers import create_inventory_setup

pytestmark = pytest.mark.manual


def test_reserve_inventory_returns_resource_busy_when_row_locked(client):
    engine = create_engine(
        "postgresql+psycopg://autoparts_user:autoparts_pass@localhost:5432/autoparts_test",
        echo=False,
    )

    setup = create_inventory_setup(
        client,
        brand_name="Pagid",
        sku="BRK-016",
        product_name="Lock Timeout Pads",
        price="77.00",
        warehouse_code="LOCK15",
        warehouse_name="Lock Timeout Warehouse",
        region="Florida",
        on_hand_qty=10,
        reserved_qty=0,
    )

    balance = setup["balance"]

    lock_started = threading.Event()
    release_lock = threading.Event()

    def locker():
        with engine.connect() as conn:
            trans = conn.begin()
            conn.execute(text("SET LOCAL lock_timeout = '30s'"))
            conn.execute(
                text("""
                    select *
                    from autoparts_owner.inventory_balance
                    where inventory_balance_id = :balance_id
                    for update
                """),
                {"balance_id": balance["inventory_balance_id"]},
            )
            lock_started.set()
            release_lock.wait(timeout=25)
            trans.rollback()

    thread = threading.Thread(target=locker, daemon=True)
    thread.start()

    assert lock_started.wait(timeout=5)

    start = time.time()
    reserve_response = client.post(
        f"/inventory-balances/{balance['inventory_balance_id']}/reserve",
        json={"qty": 1},
    )
    elapsed = time.time() - start

    release_lock.set()
    thread.join(timeout=5)

    assert reserve_response.status_code == 409
    assert reserve_response.json()["detail"] == "Resource busy, try again later."
    assert elapsed >= 10

    with engine.connect() as conn:
        movement_rows = conn.execute(
            text("""
                select movement_type
                from autoparts_owner.inventory_movement
                order by inventory_movement_id
            """)
        ).fetchall()

    assert len(movement_rows) == 1
    assert movement_rows[0][0] == "INITIAL_LOAD"
