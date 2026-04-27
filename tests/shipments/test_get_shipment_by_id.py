from tests.helpers import create_and_complete_payment, create_order_setup, reserve_order, ship_order


def test_get_shipment_by_id(client):
    setup = create_order_setup(
        client,
        sku="BRK-024",
        product_name="Shipment Read Pads",
        price="103.99",
        warehouse_code="SHPGET",
        warehouse_name="Shipment Read Warehouse",
        region="Florida",
        on_hand_qty=10,
        reserved_qty=0,
        order_number="SO-800002",
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

    get_response = client.get(f"/shipments/{shipment_id}")
    assert get_response.status_code == 200

    payload = get_response.json()
    assert payload["shipment_id"] == shipment_id
    assert payload["order_id"] == order["order_id"]
    assert payload["shipment_number"] == f"SHP-{order['order_id']:06d}"
    assert payload["shipment_status"] == "SHIPPED"
    assert payload["carrier_name"] is None
    assert payload["tracking_number"] is None
    assert payload["shipped_datetime"] is not None
