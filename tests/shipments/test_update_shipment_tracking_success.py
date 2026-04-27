from tests.helpers import create_and_complete_payment, create_order_setup, reserve_order, ship_order


def test_update_shipment_tracking_success(client):
    setup = create_order_setup(
        client,
        sku="BRK-025",
        product_name="Shipment Patch Pads",
        price="105.99",
        warehouse_code="SHPPCH",
        warehouse_name="Shipment Patch Warehouse",
        region="Florida",
        on_hand_qty=10,
        reserved_qty=0,
        order_number="SO-900001",
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

    patch_response = client.patch(
        f"/shipments/{shipment_id}",
        json={
            "carrier_name": "UPS",
            "tracking_number": "1Z999AA10123456784",
        },
    )
    assert patch_response.status_code == 200

    payload = patch_response.json()
    assert payload["shipment_id"] == shipment_id
    assert payload["order_id"] == order["order_id"]
    assert payload["shipment_status"] == "SHIPPED"
    assert payload["carrier_name"] == "UPS"
    assert payload["tracking_number"] == "1Z999AA10123456784"
    assert payload["shipment_number"] == f"SHP-{order['order_id']:06d}"
