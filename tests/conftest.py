import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.db import get_db
from app.main import app


TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://autoparts_user:autoparts_pass@localhost:5432/autoparts_test",
)

engine = create_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def override_dependency():
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function", autouse=True)
def clean_database():
    with engine.begin() as connection:
        connection.execute(text("TRUNCATE TABLE autoparts_owner.inventory_movement RESTART IDENTITY CASCADE"))
        connection.execute(text("TRUNCATE TABLE autoparts_owner.sales_order_item RESTART IDENTITY CASCADE"))
        connection.execute(text("TRUNCATE TABLE autoparts_owner.sales_order RESTART IDENTITY CASCADE"))
        connection.execute(text("TRUNCATE TABLE autoparts_owner.inventory_balance RESTART IDENTITY CASCADE"))
        connection.execute(text("TRUNCATE TABLE autoparts_owner.product RESTART IDENTITY CASCADE"))
        connection.execute(text("TRUNCATE TABLE autoparts_owner.product_category RESTART IDENTITY CASCADE"))
        connection.execute(text("TRUNCATE TABLE autoparts_owner.product_brand RESTART IDENTITY CASCADE"))
        connection.execute(text("TRUNCATE TABLE autoparts_owner.warehouse RESTART IDENTITY CASCADE"))
    yield


@pytest.fixture(scope="function")
def client():
    return TestClient(app)