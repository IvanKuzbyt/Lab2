"""Pydantic request/response schemas for warehouse API."""

from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict


class ProductCreate(BaseModel):
    code: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=255)
    quantity: int = Field(ge=0)
    unit_price: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    minimum_stock: int = Field(default=5, ge=0)


class ProductPatch(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    unit_price: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    minimum_stock: int | None = Field(default=None, ge=0)


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    code: str
    name: str
    quantity: int
    unit_price: Decimal
    minimum_stock: int


class StockChange(BaseModel):
    quantity: int = Field(gt=0)


class StockOperationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    product_id: int
    operation_type: str
    quantity: int
    quantity_after: int


class ValueOut(BaseModel):
    total_value: Decimal


class BatchRequest(BaseModel):
    product_ids: list[int] = Field(min_length=1, max_length=30)
