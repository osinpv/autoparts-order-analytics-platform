from sqlalchemy import text

from tests.helpers import create_and_complete_payment, create_order_setup, reserve_order, ship_order


def test_deliver_shipment_success(client, db_session):
    setup = create_order_setup(
        client,
        sku="BRK-026",
        product_name="Shipment Deliver Pads",
        price="107.99",
        warehouse_code="SHPDLV",
        warehouse_name="Shipment Deliver Warehouse",
        region="Florida",
        on_hand_qty=10,
        reserved_qty=0,
        order_number="SO-900002",
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

    deliver_response = client.post(f"/shipments/{shipment_id}/deliver")
    assert deliver_response.status_code == 200

    payload = deliver_response.json()
    assert payload["shipment_id"] == shipment_id
    assert payload["order_id"] == order["order_id"]
    assert payload["shipment_status"] == "DELIVERED"
    assert payload["shipment_number"] == f"SHP-{order['order_id']:06d}"

    order_row = db_session.execute(
        text("""
            select order_status
            from autoparts_owner.sales_order
            where order_id = :order_id
        """),
        {"order_id": order["order_id"]},
    ).fetchone()

    assert order_row is not None
    assert order_row[0] == "DELIVERED"
