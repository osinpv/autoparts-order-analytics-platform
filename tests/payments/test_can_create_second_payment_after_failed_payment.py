from tests.helpers import create_order_setup


def test_can_create_second_payment_after_failed_payment(client):
    setup = create_order_setup(
        client,
        sku="BRK-038",
        product_name="Second Failed Payment Pads",
        price="121.99",
        warehouse_code="PAYFAIL2",
        warehouse_name="Second Failed Payment Warehouse",
        region="Florida",
        on_hand_qty=10,
        reserved_qty=0,
        order_number="SO-1000011",
        customer_email="john@example.com",
        order_qty=2,
    )

    order = setup["order"]

    first_response = client.post(
        f"/orders/{order['order_id']}/payments",
        json={"payment_method": "CARD"},
    )
    assert first_response.status_code == 200
    assert first_response.json()["payment_number"] == f"PAY-{order['order_id']:06d}-01"
    first_payment_id = first_response.json()["payment_id"]

    fail_response = client.post(f"/payments/{first_payment_id}/fail")
    assert fail_response.status_code == 200
    assert fail_response.json()["payment_status"] == "FAILED"

    second_response = client.post(
        f"/orders/{order['order_id']}/payments",
        json={"payment_method": "PAYPAL"},
    )
    assert second_response.status_code == 200

    payload = second_response.json()
    assert payload["order_id"] == order["order_id"]
    assert payload["payment_number"] == f"PAY-{order['order_id']:06d}-02"
    assert payload["payment_status"] == "PENDING"
    assert payload["payment_method"] == "PAYPAL"
    assert payload["amount"] == "243.98"
    assert payload["paid_datetime"] is None
