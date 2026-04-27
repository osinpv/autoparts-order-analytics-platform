def create_category(client, category_name="Brakes", parent_category_id=None):
    response = client.post(
        "/categories",
        json={
            "category_name": category_name,
            "parent_category_id": parent_category_id,
        },
    )
    assert response.status_code == 200
    return response.json()


def create_brand(client, brand_name="Brembo"):
    response = client.post(
        "/brands",
        json={
            "brand_name": brand_name,
        },
    )
    assert response.status_code == 200
    return response.json()


def create_product(
    client,
    sku="BRK-001",
    product_name="Brake Pads",
    category_id=None,
    brand_id=None,
    price="79.99",
    is_active=True,
):
    response = client.post(
        "/products",
        json={
            "sku": sku,
            "product_name": product_name,
            "category_id": category_id,
            "brand_id": brand_id,
            "price": price,
            "is_active": is_active,
        },
    )
    assert response.status_code == 200
    return response.json()


def create_warehouse(
    client,
    warehouse_code="TPA",
    warehouse_name="Tampa Warehouse",
    region="Florida West",
):
    response = client.post(
        "/warehouses",
        json={
            "warehouse_code": warehouse_code,
            "warehouse_name": warehouse_name,
            "region": region,
        },
    )
    assert response.status_code == 200
    return response.json()


def create_inventory_balance(
    client,
    warehouse_id,
    product_id,
    on_hand_qty=10,
    reserved_qty=0,
):
    response = client.post(
        "/inventory-balances",
        json={
            "warehouse_id": warehouse_id,
            "product_id": product_id,
            "on_hand_qty": on_hand_qty,
            "reserved_qty": reserved_qty,
        },
    )
    assert response.status_code == 200
    return response.json()


def create_order(
    client,
    order_number="SO-100001",
    customer_email="john@example.com",
    items=None,
):
    if items is None:
        items = []

    response = client.post(
        "/orders",
        json={
            "order_number": order_number,
            "customer_email": customer_email,
            "items": items,
        },
    )
    assert response.status_code == 200
    return response.json()


def reserve_order(client, order_id):
    response = client.post(f"/orders/{order_id}/reserve")
    assert response.status_code == 200
    return response.json()


def release_order(client, order_id):
    response = client.post(f"/orders/{order_id}/release")
    assert response.status_code == 200
    return response.json()


def ship_order(client, order_id):
    response = client.post(f"/orders/{order_id}/ship")
    assert response.status_code == 200
    return response.json()


def create_and_complete_payment(client, order_id, payment_method="CARD"):
    create_response = client.post(
        f"/orders/{order_id}/payments",
        json={"payment_method": payment_method},
    )
    assert create_response.status_code == 200
    payment_id = create_response.json()["payment_id"]

    complete_response = client.post(f"/payments/{payment_id}/complete")
    assert complete_response.status_code == 200
    assert complete_response.json()["payment_status"] == "PAID"

    return complete_response.json()


def create_basic_catalog_setup(
    client,
    *,
    category_name="Brakes",
    brand_name="Brembo",
    sku="BRK-001",
    product_name="Brake Pads",
    price="79.99",
    is_active=True,
    warehouse_code="TPA",
    warehouse_name="Tampa Warehouse",
    region="Florida West",
):
    category = create_category(client, category_name=category_name)
    brand = create_brand(client, brand_name=brand_name)
    product = create_product(
        client,
        sku=sku,
        product_name=product_name,
        category_id=category["category_id"],
        brand_id=brand["brand_id"],
        price=price,
        is_active=is_active,
    )
    warehouse = create_warehouse(
        client,
        warehouse_code=warehouse_code,
        warehouse_name=warehouse_name,
        region=region,
    )

    return {
        "category": category,
        "brand": brand,
        "product": product,
        "warehouse": warehouse,
    }


def create_inventory_setup(
    client,
    *,
    category_name="Brakes",
    brand_name="Brembo",
    sku="BRK-001",
    product_name="Brake Pads",
    price="79.99",
    is_active=True,
    warehouse_code="TPA",
    warehouse_name="Tampa Warehouse",
    region="Florida West",
    on_hand_qty=10,
    reserved_qty=0,
):
    setup = create_basic_catalog_setup(
        client,
        category_name=category_name,
        brand_name=brand_name,
        sku=sku,
        product_name=product_name,
        price=price,
        is_active=is_active,
        warehouse_code=warehouse_code,
        warehouse_name=warehouse_name,
        region=region,
    )

    balance = create_inventory_balance(
        client,
        warehouse_id=setup["warehouse"]["warehouse_id"],
        product_id=setup["product"]["product_id"],
        on_hand_qty=on_hand_qty,
        reserved_qty=reserved_qty,
    )

    setup["balance"] = balance
    return setup


def create_order_setup(
    client,
    *,
    category_name="Brakes",
    brand_name="Brembo",
    sku="BRK-001",
    product_name="Brake Pads",
    price="79.99",
    is_active=True,
    warehouse_code="TPA",
    warehouse_name="Tampa Warehouse",
    region="Florida West",
    on_hand_qty=10,
    reserved_qty=0,
    order_number="SO-100001",
    customer_email="john@example.com",
    order_qty=2,
):
    setup = create_inventory_setup(
        client,
        category_name=category_name,
        brand_name=brand_name,
        sku=sku,
        product_name=product_name,
        price=price,
        is_active=is_active,
        warehouse_code=warehouse_code,
        warehouse_name=warehouse_name,
        region=region,
        on_hand_qty=on_hand_qty,
        reserved_qty=reserved_qty,
    )

    order = create_order(
        client,
        order_number=order_number,
        customer_email=customer_email,
        items=[
            {
                "product_id": setup["product"]["product_id"],
                "warehouse_id": setup["warehouse"]["warehouse_id"],
                "qty": order_qty,
            }
        ],
    )

    setup["order"] = order
    return setup
