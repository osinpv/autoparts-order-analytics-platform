from sqlalchemy import text

from tests.helpers import create_basic_catalog_setup, create_order


def test_create_order_uses_product_price(client, db_session):
    setup = create_basic_catalog_setup(
        client,
        sku="BRK-003",
        product_name="Ceramic Brake Pads",
        price="79.99",
        warehouse_code="ORL",
        warehouse_name="Orlando Warehouse",
        region="Florida Central",
    )

    order = create_order(
        client,
        order_number="SO-200001",
        customer_email="john@example.com",
        items=[
            {
                "product_id": setup["product"]["product_id"],
                "warehouse_id": setup["warehouse"]["warehouse_id"],
                "qty": 2,
            }
        ],
    )

    assert order["order_number"] == "SO-200001"
    assert order["customer_email"] == "john@example.com"
    assert order["order_status"] == "NEW"
    assert order["order_total_amount"] == "159.98"

    item_row = db_session.execute(
        text("""
            select product_id, warehouse_id, qty, unit_price, line_amount
            from autoparts_owner.sales_order_item
            where order_id = :order_id
        """),
        {"order_id": order["order_id"]},
    ).fetchone()

    assert item_row is not None
    assert item_row[0] == setup["product"]["product_id"]
    assert item_row[1] == setup["warehouse"]["warehouse_id"]
    assert item_row[2] == 2
    assert str(item_row[3]) == "79.99"
    assert str(item_row[4]) == "159.98"

    order_row = db_session.execute(
        text("""
            select order_status, order_total_amount
            from autoparts_owner.sales_order
            where order_id = :order_id
        """),
        {"order_id": order["order_id"]},
    ).fetchone()

    assert order_row is not None
    assert order_row[0] == "NEW"
    assert str(order_row[1]) == "159.98"
