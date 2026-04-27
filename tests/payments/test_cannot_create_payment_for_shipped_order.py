from tests.helpers import create_and_complete_payment, create_order_setup, reserve_order, ship_order


def test_cannot_create_payment_for_shipped_order(client):
    setup = create_order_setup(
        client,
        sku="BRK-033",
        product_name="Payment After Ship Pads",
        price="116.99",
        warehouse_code="PAYSHP",
        warehouse_name="Payment After Ship Warehouse",
        region="Florida",
        on_hand_qty=10,
        reserved_qty=0,
        order_number="SO-1000005",
        customer_email="john@example.com",
        order_qty=2,
    )

    order = setup["order"]

    reserve_payload = reserve_order(client, order["order_id"])
    assert reserve_payload["order_status"] == "RESERVED"

    create_and_complete_payment(client, order["order_id"])
    ship_payload = ship_order(client, order["order_id"])
    assert ship_payload["order_status"] == "SHIPPED"

    response = client.post(
        f"/orders/{order['order_id']}/payments",
        json={"payment_method": "CARD"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Payments can only be created for orders in NEW, RESERVED, or RELEASED status."
