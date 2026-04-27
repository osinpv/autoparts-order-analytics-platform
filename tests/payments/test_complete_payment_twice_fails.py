from tests.helpers import create_order_setup


def test_complete_payment_twice_fails(client):
    setup = create_order_setup(
        client,
        sku="BRK-032",
        product_name="Payment Complete Twice Pads",
        price="115.99",
        warehouse_code="PAY2X",
        warehouse_name="Payment Complete Twice Warehouse",
        region="Florida",
        on_hand_qty=10,
        reserved_qty=0,
        order_number="SO-1000004",
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

    first_complete_response = client.post(f"/payments/{payment_id}/complete")
    assert first_complete_response.status_code == 200
    assert first_complete_response.json()["payment_status"] == "PAID"

    second_complete_response = client.post(f"/payments/{payment_id}/complete")
    assert second_complete_response.status_code == 400
    assert second_complete_response.json()["detail"] == "Only payments in PENDING status can be completed."
