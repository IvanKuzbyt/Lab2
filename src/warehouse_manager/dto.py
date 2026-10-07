"""Typed data-transfer objects for external operation payloads."""

from typing import TypedDict
from typing_extensions import NotRequired


class StockOperationPayload(TypedDict):
    operation_id: int
    code: str
    operation: str
    quantity: int
    note: NotRequired[str]
