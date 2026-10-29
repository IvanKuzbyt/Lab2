"""Lab 8: FastAPI over the Lab 7 SQLAlchemy repository and transaction service."""

import logging
from .config import get_settings
from collections.abc import Generator
from typing import cast
from fastapi import Depends, FastAPI, HTTPException, Query, Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .database import make_engine, make_session_factory
from .models import Base, StockOperationRecord, ProductRecord
from .repositories import ProductRepository, StockOperationRepository
from .services import InsufficientStockError, change_stock
from .schemas import ProductCreate, ProductPatch, ProductOut, StockChange, StockOperationOut, ValueOut, BatchRequest
from .external_api import fetch_many_products

settings = get_settings()
logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))
logger = logging.getLogger(__name__)
app = FastAPI(title=settings.app_name, version="1.0.0", description="Variant 10: inventory and stock movements")


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    return {"status": "ok", "environment": get_settings().app_env}


def get_session() -> Generator[Session, None, None]:
    engine = make_engine(get_settings().database_url)
    Base.metadata.create_all(engine)
    with make_session_factory(engine)() as session:
        yield session
    engine.dispose()


def require_product(repo: ProductRepository, product_id: int) -> ProductRecord:
    product = repo.get(product_id)
    if product is None:
        raise HTTPException(404, "Product not found")
    return cast(ProductRecord, product)


@app.get("/", tags=["system"])
async def root() -> dict[str, str]:
    return {"message": "Warehouse API is running"}


@app.get("/products", response_model=list[ProductOut], tags=["products"])
async def list_products(
    name: str | None = None,
    code: str | None = None,
    limit: int = Query(100, ge=1, le=500),
    session: Session = Depends(get_session),
) -> list[ProductRecord]:
    repo = ProductRepository(session)
    products = [repo.by_code(code)] if code else repo.by_name(name) if name else repo.all()
    return [p for p in products if p is not None][:limit]


@app.get("/products/low-stock", response_model=list[ProductOut], tags=["stock"])
async def low_stock(session: Session = Depends(get_session)) -> list[ProductRecord]:
    return cast(list[ProductRecord], ProductRepository(session).low_stock())


@app.get("/products/{product_id}", response_model=ProductOut, tags=["products"])
async def get_product(product_id: int, session: Session = Depends(get_session)) -> ProductRecord:
    return require_product(ProductRepository(session), product_id)


@app.post("/products", response_model=ProductOut, status_code=201, tags=["products"])
async def create_product(data: ProductCreate, session: Session = Depends(get_session)) -> ProductRecord:
    try:
        return cast(ProductRecord, ProductRepository(session).add(**data.model_dump()))
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, "Product code already exists")


@app.patch("/products/{product_id}", response_model=ProductOut, tags=["products"])
async def patch_product(product_id: int, data: ProductPatch, session: Session = Depends(get_session)) -> ProductRecord | None:
    repo = ProductRepository(session)
    require_product(repo, product_id)
    return cast(ProductRecord | None, repo.update(product_id, **data.model_dump(exclude_unset=True)))


@app.delete("/products/{product_id}", status_code=204, tags=["products"])
async def delete_product(product_id: int, session: Session = Depends(get_session)) -> Response:
    if not ProductRepository(session).delete(product_id):
        raise HTTPException(404, "Product not found")
    return Response(status_code=204)


def apply_movement(session: Session, product_id: int, operation_type: str, amount: int) -> StockOperationRecord:
    try:
        return cast(StockOperationRecord, change_stock(session, product_id, operation_type, amount))
    except LookupError:
        raise HTTPException(404, "Product not found")
    except InsufficientStockError:
        raise HTTPException(409, "Insufficient stock")


@app.post("/products/{product_id}/incoming", response_model=StockOperationOut, status_code=201, tags=["stock"])
async def incoming(product_id: int, data: StockChange, session: Session = Depends(get_session)) -> StockOperationRecord:
    return apply_movement(session, product_id, "receipt", data.quantity)


@app.post("/products/{product_id}/write-off", response_model=StockOperationOut, status_code=201, tags=["stock"])
async def write_off(product_id: int, data: StockChange, session: Session = Depends(get_session)) -> StockOperationRecord:
    return apply_movement(session, product_id, "write_off", data.quantity)


@app.get("/stock/operations", response_model=list[StockOperationOut], tags=["stock"])
async def operations(product_id: int | None = None, session: Session = Depends(get_session)) -> list[StockOperationRecord]:
    from sqlalchemy import select

    if product_id is not None:
        return cast(list[StockOperationRecord], StockOperationRepository(session).history(product_id))
    return list(session.scalars(select(StockOperationRecord).order_by(StockOperationRecord.id)))


@app.get("/stock/value", response_model=ValueOut, tags=["stock"])
async def stock_value(session: Session = Depends(get_session)) -> ValueOut:
    return ValueOut(total_value=ProductRepository(session).total_value())


@app.post("/products/batch-check", response_model=list[ProductOut], tags=["async"])
async def batch_check(data: BatchRequest, base_url: str = "http://127.0.0.1:8000") -> list[ProductOut]:
    try:
        return cast(list[ProductOut], await fetch_many_products(base_url, data.product_ids))
    except TimeoutError:
        raise HTTPException(504, "Batch request timed out")
    except Exception as exc:
        import httpx

        if isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code == 404:
            raise HTTPException(404, "One of the products was not found")
        if isinstance(exc, httpx.RequestError):
            raise HTTPException(503, "Upstream API unavailable")
        raise
