from tests.helpers import create_order_setup


def test_cannot_create_second_payment_while_paid_payment_exists(client):
    setup = create_order_setup(
        client,
        sku="BRK-037",
        product_name="Second Paid Payment Pads",
        price="120.99",
        warehouse_code="PAYPAID2",
        warehouse_name="Second Paid Payment Warehouse",
        region="Florida",
        on_hand_qty=10,
        reserved_qty=0,
        order_number="SO-1000010",
        customer_email="john@example.com",
        order_qty=2,
    )

    order = setup["order"]

    first_response = client.post(
        f"/orders/{order['order_id']}/payments",
        json={"payment_method": "CARD"},
    )
    assert first_response.status_code == 200
    payment_id = first_response.json()["payment_id"]

    complete_response = client.post(f"/payments/{payment_id}/complete")
    assert complete_response.status_code == 200
    assert complete_response.json()["payment_status"] == "PAID"

    second_response = client.post(
        f"/orders/{order['order_id']}/payments",
        json={"payment_method": "PAYPAL"},
    )
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Cannot create a new payment while the order has an active PENDING or PAID payment."
