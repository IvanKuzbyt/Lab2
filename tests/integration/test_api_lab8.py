"""Lab 8: API integration tests with isolated SQLite persistence."""

import httpx
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from warehouse_persistence.api import app, get_session
from warehouse_persistence.models import Base
from warehouse_persistence.external_api import fetch_many_products


@pytest.fixture
def client(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'test_lab8.db'}")

    @event.listens_for(engine, "connect")
    def fk_on(dbapi_conn, _):
        dbapi_conn.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

    def override():
        with SessionLocal() as session:
            yield session

    app.dependency_overrides[get_session] = override
    from fastapi.testclient import TestClient

    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    engine.dispose()


@pytest.fixture
def product(client):
    r = client.post(
        "/products",
        json={"code": "TEST-01", "name": "Widget", "quantity": 10, "unit_price": "12.50", "minimum_stock": 5},
    )
    assert r.status_code == 201, r.text
    return r.json()


def test_root(client):
    assert client.get("/").status_code == 200


def test_swagger(client):
    assert client.get("/openapi.json").status_code == 200


def test_create_and_get(client, product):
    assert client.get(f"/products/{product['id']}").json()["code"] == "TEST-01"


def test_list_and_query(client, product):
    assert len(client.get("/products?name=Wid").json()) == 1
    assert len(client.get("/products?code=TEST-01").json()) == 1
    assert client.get("/products?limit=0").status_code == 422


def test_patch(client, product):
    r = client.patch(f"/products/{product['id']}", json={"unit_price": "15.00"})
    assert r.status_code == 200 and float(r.json()["unit_price"]) == 15


def test_delete(client, product):
    assert client.delete(f"/products/{product['id']}").status_code == 204
    assert client.get(f"/products/{product['id']}").status_code == 404


def test_duplicate_conflict(client, product):
    assert (
        client.post(
            "/products", json={"code": "TEST-01", "name": "Other", "quantity": 1, "unit_price": "1"}
        ).status_code
        == 409
    )


def test_validation(client):
    assert (
        client.post("/products", json={"code": "", "name": "", "quantity": -1, "unit_price": "-1"}).status_code == 422
    )


def test_stock_and_history(client, product):
    pid = product["id"]
    assert client.post(f"/products/{pid}/incoming", json={"quantity": 4}).json()["quantity_after"] == 14
    assert client.post(f"/products/{pid}/write-off", json={"quantity": 2}).json()["quantity_after"] == 12
    assert len(client.get(f"/stock/operations?product_id={pid}").json()) == 2
    assert len(client.get("/stock/operations").json()) == 2
    assert float(client.get("/stock/value").json()["total_value"]) == 150


def test_insufficient_stock_rolls_back(client, product):
    pid = product["id"]
    assert client.post(f"/products/{pid}/write-off", json={"quantity": 999}).status_code == 409
    assert client.get(f"/products/{pid}").json()["quantity"] == 10
    assert client.get("/stock/operations").json() == []


def test_low_stock(client, product):
    pid = product["id"]
    assert client.get("/products/low-stock").json() == []
    assert client.post(f"/products/{pid}/write-off", json={"quantity": 6}).status_code == 201
    assert len(client.get("/products/low-stock").json()) == 1


def test_missing_and_invalid(client):
    assert client.get("/products/999").status_code == 404
    assert client.delete("/products/999").status_code == 404
    assert client.post("/products/999/incoming", json={"quantity": 1}).status_code == 404
    assert client.post("/products/999/write-off", json={"quantity": 0}).status_code == 422


@pytest.mark.asyncio
async def test_httpx_asyncclient(client, product):
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as async_client:
        r = await async_client.get(f"/products/{product['id']}")
        assert r.status_code == 200


@pytest.mark.asyncio
async def test_concurrent_batch(client, product):
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as async_client:
        rows = await fetch_many_products("http://test", [product["id"]] * 4, max_concurrent=2, client=async_client)
        assert len(rows) == 4 and all(row["code"] == "TEST-01" for row in rows)


@pytest.mark.asyncio
async def test_retry_httpx(client, product):
    count = 0

    async def handler(request):
        nonlocal count
        count += 1
        if count == 1:
            return httpx.Response(503, json={"detail": "try again"})
        return httpx.Response(200, json=product)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://test") as c:
        rows = await fetch_many_products("http://test", [product["id"]], attempts=2, client=c)
        assert rows[0]["id"] == product["id"] and count == 2
