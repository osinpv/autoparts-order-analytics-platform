from tests.helpers import create_order_setup


def test_get_payment_by_id(client):
    setup = create_order_setup(
        client,
        sku="BRK-035",
        product_name="Payment Read By Id Pads",
        price="118.99",
        warehouse_code="PAYID",
        warehouse_name="Payment Read By Id Warehouse",
        region="Florida",
        on_hand_qty=10,
        reserved_qty=0,
        order_number="SO-1000007",
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

    get_response = client.get(f"/payments/{payment_id}")
    assert get_response.status_code == 200

    payload = get_response.json()
    assert payload["payment_id"] == payment_id
    assert payload["order_id"] == order["order_id"]
    assert payload["payment_number"] == f"PAY-{order['order_id']:06d}-01"
    assert payload["payment_status"] == "PENDING"
    assert payload["payment_method"] == "CARD"
    assert payload["amount"] == "237.98"
