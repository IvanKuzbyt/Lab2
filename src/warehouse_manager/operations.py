"""Polymorphic stock operations."""

from abc import ABC, abstractmethod

from warehouse_manager.models import StockOperationResult, Warehouse


class StockOperation(ABC):
    """Abstract operation with a shared execution contract."""

    def __init__(self, operation_id: int, code: str, quantity: int) -> None:
        if operation_id <= 0 or not code.strip() or quantity <= 0:
            raise ValueError("Некоректні параметри складської операції")
        self.operation_id = operation_id
        self.code = code.upper()
        self.quantity = quantity

    @abstractmethod
    def execute(self, warehouse: Warehouse) -> StockOperationResult:
        """Apply the operation and return a result."""


class ReceiptOperation(StockOperation):
    def execute(self, warehouse: Warehouse) -> StockOperationResult:
        item = warehouse.find_by_code(self.code)
        if item is None:
            raise KeyError(f"Товар {self.code} не знайдено")
        item.receive(self.quantity)
        return StockOperationResult(self.operation_id, self.code, "надходження",
                                    self.quantity, item.quantity)


class WriteOffOperation(StockOperation):
    def execute(self, warehouse: Warehouse) -> StockOperationResult:
        item = warehouse.find_by_code(self.code)
        if item is None:
            raise KeyError(f"Товар {self.code} не знайдено")
        item.write_off(self.quantity)
        return StockOperationResult(self.operation_id, self.code, "списання",
                                    self.quantity, item.quantity)
