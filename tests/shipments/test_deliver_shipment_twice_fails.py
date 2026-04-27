from tests.helpers import create_and_complete_payment, create_order_setup, reserve_order, ship_order


def test_deliver_shipment_twice_fails(client):
    setup = create_order_setup(
        client,
        sku="BRK-027",
        product_name="Shipment Deliver Twice Pads",
        price="109.99",
        warehouse_code="SHP2X",
        warehouse_name="Shipment Deliver Twice Warehouse",
        region="Florida",
        on_hand_qty=10,
        reserved_qty=0,
        order_number="SO-900003",
        customer_email="john@example.com",
        order_qty=2,
    )

    order = setup["order"]

    reserve_payload = reserve_order(client, order["order_id"])
    assert reserve_payload["order_status"] == "RESERVED"

    create_and_complete_payment(client, order["order_id"])
    ship_payload = ship_order(client, order["order_id"])
    assert ship_payload["order_status"] == "SHIPPED"

    list_response = client.get(f"/shipments?order_id={order['order_id']}")
    assert list_response.status_code == 200
    shipments = list_response.json()
    assert len(shipments) == 1

    shipment_id = shipments[0]["shipment_id"]

    first_deliver_response = client.post(f"/shipments/{shipment_id}/deliver")
    assert first_deliver_response.status_code == 200
    assert first_deliver_response.json()["shipment_status"] == "DELIVERED"

    second_deliver_response = client.post(f"/shipments/{shipment_id}/deliver")
    assert second_deliver_response.status_code == 400
    assert second_deliver_response.json()["detail"] == "Shipment is already delivered."
