from tests.helpers import create_order_setup


def test_create_payment_for_order_success(client):
    setup = create_order_setup(
        client,
        sku="BRK-029",
        product_name="Payment Create Pads",
        price="112.99",
        warehouse_code="PAYCRT",
        warehouse_name="Payment Create Warehouse",
        region="Florida",
        on_hand_qty=10,
        reserved_qty=0,
        order_number="SO-1000001",
        customer_email="john@example.com",
        order_qty=2,
    )

    order = setup["order"]

    response = client.post(
        f"/orders/{order['order_id']}/payments",
        json={"payment_method": "CARD"},
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["order_id"] == order["order_id"]
    assert payload["payment_number"] == f"PAY-{order['order_id']:06d}-01"
    assert payload["payment_status"] == "PENDING"
    assert payload["payment_method"] == "CARD"
    assert payload["amount"] == "225.98"
    assert payload["paid_datetime"] is None
