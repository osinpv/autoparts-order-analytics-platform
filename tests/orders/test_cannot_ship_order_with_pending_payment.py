from tests.helpers import create_order_setup, reserve_order


def test_cannot_ship_order_with_pending_payment(client):
    setup = create_order_setup(
        client,
        sku="BRK-037",
        product_name="Ship Pending Payment Pads",
        price="120.99",
        warehouse_code="PNDPAY",
        warehouse_name="Pending Payment Warehouse",
        region="Florida",
        on_hand_qty=10,
        reserved_qty=0,
        order_number="SO-1100002",
        customer_email="john@example.com",
        order_qty=2,
    )

    order = setup["order"]

    reserve_payload = reserve_order(client, order["order_id"])
    assert reserve_payload["order_status"] == "RESERVED"

    create_payment_response = client.post(
        f"/orders/{order['order_id']}/payments",
        json={"payment_method": "CARD"},
    )
    assert create_payment_response.status_code == 200
    assert create_payment_response.json()["payment_status"] == "PENDING"

    ship_response = client.post(f"/orders/{order['order_id']}/ship")
    assert ship_response.status_code == 400
    assert ship_response.json()["detail"] == "Order must have a PAID payment before shipment."
