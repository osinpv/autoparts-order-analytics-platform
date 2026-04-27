from tests.helpers import create_order_setup


def test_get_payments_by_order_id(client):
    setup = create_order_setup(
        client,
        sku="BRK-034",
        product_name="Payment Read Pads",
        price="117.99",
        warehouse_code="PAYGET",
        warehouse_name="Payment Read Warehouse",
        region="Florida",
        on_hand_qty=10,
        reserved_qty=0,
        order_number="SO-1000006",
        customer_email="john@example.com",
        order_qty=2,
    )

    order = setup["order"]

    create_response = client.post(
        f"/orders/{order['order_id']}/payments",
        json={"payment_method": "BANK_TRANSFER"},
    )
    assert create_response.status_code == 200

    list_response = client.get(f"/payments?order_id={order['order_id']}")
    assert list_response.status_code == 200

    payload = list_response.json()
    assert len(payload) == 1

    payment = payload[0]
    assert payment["order_id"] == order["order_id"]
    assert payment["payment_number"] == f"PAY-{order['order_id']:06d}-01"
    assert payment["payment_status"] == "PENDING"
    assert payment["payment_method"] == "BANK_TRANSFER"
