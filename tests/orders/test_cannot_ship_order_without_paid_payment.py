from tests.helpers import create_order_setup, reserve_order


def test_cannot_ship_order_without_payment(client):
    setup = create_order_setup(
        client,
        sku="BRK-036",
        product_name="Ship Without Payment Pads",
        price="119.99",
        warehouse_code="NOPAY",
        warehouse_name="No Payment Warehouse",
        region="Florida",
        on_hand_qty=10,
        reserved_qty=0,
        order_number="SO-1100001",
        customer_email="john@example.com",
        order_qty=2,
    )

    order = setup["order"]

    reserve_payload = reserve_order(client, order["order_id"])
    assert reserve_payload["order_status"] == "RESERVED"

    ship_response = client.post(f"/orders/{order['order_id']}/ship")
    assert ship_response.status_code == 400
    assert ship_response.json()["detail"] == "Order must have a PAID payment before shipment."
