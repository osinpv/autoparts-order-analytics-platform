from sqlalchemy import text

from tests.helpers import create_warehouse


def test_create_order_with_missing_product_fails(client, db_session):
    warehouse = create_warehouse(
        client,
        warehouse_code="ORDNEG",
        warehouse_name="Order Negative Warehouse",
        region="Florida",
    )

    order_response = client.post(
        "/orders",
        json={
            "order_number": "SO-500001",
            "customer_email": "john@example.com",
            "items": [
                {
                    "product_id": 99999,
                    "warehouse_id": warehouse["warehouse_id"],
                    "qty": 2,
                }
            ],
        },
    )

    assert order_response.status_code == 404
    assert order_response.json()["detail"] == "Product not found: product_id=99999."

    count = db_session.execute(
        text("select count(*) from autoparts_owner.sales_order")
    ).scalar_one()

    assert count == 0


def test_create_order_requires_at_least_one_item(client, db_session):
    order_response = client.post(
        "/orders",
        json={
            "order_number": "SO-500002",
            "customer_email": "john@example.com",
            "items": [],
        },
    )

    assert order_response.status_code == 422

    count = db_session.execute(
        text("select count(*) from autoparts_owner.sales_order")
    ).scalar_one()

    assert count == 0
