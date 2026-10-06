from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class InventoryRecord:
    code: str
    name: str
    quantity: int
    price: float
    category: str


@dataclass(frozen=True, slots=True)
class StockOperation:
    code: str
    operation: str
    quantity: int
