from tests.helpers import create_and_complete_payment, create_order_setup, reserve_order, ship_order


def test_get_shipments_by_order_id(client):
    setup = create_order_setup(
        client,
        sku="BRK-023",
        product_name="Shipment Filter Pads",
        price="101.99",
        warehouse_code="SHPFLT",
        warehouse_name="Shipment Filter Warehouse",
        region="Florida",
        on_hand_qty=10,
        reserved_qty=0,
        order_number="SO-800001",
        customer_email="john@example.com",
        order_qty=2,
    )

    order = setup["order"]

    reserve_payload = reserve_order(client, order["order_id"])
    assert reserve_payload["order_status"] == "RESERVED"

    create_and_complete_payment(client, order["order_id"])
    ship_payload = ship_order(client, order["order_id"])
    assert ship_payload["order_status"] == "SHIPPED"

    response = client.get(f"/shipments?order_id={order['order_id']}")
    assert response.status_code == 200

    payload = response.json()
    assert len(payload) == 1

    shipment = payload[0]
    assert shipment["order_id"] == order["order_id"]
    assert shipment["shipment_number"] == f"SHP-{order['order_id']:06d}"
    assert shipment["shipment_status"] == "SHIPPED"
    assert shipment["carrier_name"] is None
    assert shipment["tracking_number"] is None
