from tests.helpers import create_order_setup


def test_fail_payment_success(client):
    setup = create_order_setup(
        client,
        sku="BRK-031",
        product_name="Payment Fail Pads",
        price="114.99",
        warehouse_code="PAYFAIL",
        warehouse_name="Payment Fail Warehouse",
        region="Florida",
        on_hand_qty=10,
        reserved_qty=0,
        order_number="SO-1000003",
        customer_email="john@example.com",
        order_qty=2,
    )

    order = setup["order"]

    create_response = client.post(
        f"/orders/{order['order_id']}/payments",
        json={"payment_method": "PAYPAL"},
    )
    assert create_response.status_code == 200
    payment_id = create_response.json()["payment_id"]

    fail_response = client.post(f"/payments/{payment_id}/fail")
    assert fail_response.status_code == 200

    payload = fail_response.json()
    assert payload["payment_id"] == payment_id
    assert payload["order_id"] == order["order_id"]
    assert payload["payment_status"] == "FAILED"
    assert payload["payment_method"] == "PAYPAL"
    assert payload["amount"] == "229.98"
    assert payload["payment_number"] == f"PAY-{order['order_id']:06d}-01"
    assert payload["paid_datetime"] is None
