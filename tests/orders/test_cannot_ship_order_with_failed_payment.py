from tests.helpers import create_order_setup, reserve_order


def test_cannot_ship_order_with_failed_payment(client):
    setup = create_order_setup(
        client,
        sku="BRK-038",
        product_name="Ship Failed Payment Pads",
        price="121.99",
        warehouse_code="FLDPAY",
        warehouse_name="Failed Payment Warehouse",
        region="Florida",
        on_hand_qty=10,
        reserved_qty=0,
        order_number="SO-1100003",
        customer_email="john@example.com",
        order_qty=2,
    )

    order = setup["order"]

    reserve_payload = reserve_order(client, order["order_id"])
    assert reserve_payload["order_status"] == "RESERVED"

    create_payment_response = client.post(
        f"/orders/{order['order_id']}/payments",
        json={"payment_method": "CARD"},
    )
    assert create_payment_response.status_code == 200
    payment_id = create_payment_response.json()["payment_id"]

    fail_payment_response = client.post(f"/payments/{payment_id}/fail")
    assert fail_payment_response.status_code == 200
    assert fail_payment_response.json()["payment_status"] == "FAILED"

    ship_response = client.post(f"/orders/{order['order_id']}/ship")
    assert ship_response.status_code == 400
    assert ship_response.json()["detail"] == "Order must have a PAID payment before shipment."
