from tests.helpers import create_order_setup


def test_cannot_create_second_payment_while_first_is_pending(client):
    setup = create_order_setup(
        client,
        sku="BRK-036",
        product_name="Second Pending Payment Pads",
        price="119.99",
        warehouse_code="PAYPND2",
        warehouse_name="Second Pending Payment Warehouse",
        region="Florida",
        on_hand_qty=10,
        reserved_qty=0,
        order_number="SO-1000009",
        customer_email="john@example.com",
        order_qty=2,
    )

    order = setup["order"]

    first_response = client.post(
        f"/orders/{order['order_id']}/payments",
        json={"payment_method": "CARD"},
    )
    assert first_response.status_code == 200
    assert first_response.json()["payment_status"] == "PENDING"

    second_response = client.post(
        f"/orders/{order['order_id']}/payments",
        json={"payment_method": "PAYPAL"},
    )
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Cannot create a new payment while the order has an active PENDING or PAID payment."
