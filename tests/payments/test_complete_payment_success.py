from tests.helpers import create_order_setup


def test_complete_payment_success(client):
    setup = create_order_setup(
        client,
        sku="BRK-030",
        product_name="Payment Complete Pads",
        price="113.99",
        warehouse_code="PAYOK",
        warehouse_name="Payment Complete Warehouse",
        region="Florida",
        on_hand_qty=10,
        reserved_qty=0,
        order_number="SO-1000002",
        customer_email="john@example.com",
        order_qty=2,
    )

    order = setup["order"]

    create_response = client.post(
        f"/orders/{order['order_id']}/payments",
        json={"payment_method": "CARD"},
    )
    assert create_response.status_code == 200
    payment_id = create_response.json()["payment_id"]

    complete_response = client.post(f"/payments/{payment_id}/complete")
    assert complete_response.status_code == 200

    payload = complete_response.json()
    assert payload["payment_id"] == payment_id
    assert payload["order_id"] == order["order_id"]
    assert payload["payment_status"] == "PAID"
    assert payload["payment_method"] == "CARD"
    assert payload["amount"] == "227.98"
    assert payload["payment_number"] == f"PAY-{order['order_id']:06d}-01"
    assert payload["paid_datetime"] is not None
