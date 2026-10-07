
"""Application services and interchangeable policies."""

from dataclasses import dataclass

from warehouse_manager.dto import StockOperationPayload
from warehouse_manager.models import (
    StockOperationResult,
    Warehouse,
    WarehouseItem,
)
from warehouse_manager.operations import (
    ReceiptOperation,
    StockOperation,
    WriteOffOperation,
)
from warehouse_manager.protocols import ReorderPolicy, ReportService


@dataclass(frozen=True, slots=True)
class ThresholdReorderPolicy:
    """Policy that recommends replenishment below a threshold."""

    threshold: int = 5
    target_quantity: int = 20

    def __post_init__(self) -> None:
        if self.threshold < 0 or self.target_quantity <= self.threshold:
            raise ValueError("Цільовий запас має бути більшим за поріг")

    def should_reorder(self, item: WarehouseItem) -> bool:
        return item.quantity <= self.threshold

    def recommended_quantity(self, item: WarehouseItem) -> int:
        return max(0, self.target_quantity - item.quantity)


class ConsoleReportService:
    """Renders inventory reports as plain text."""

    def render(self, title: str, lines: list[str]) -> str:
        separator = "=" * max(12, len(title))
        return "\n".join([title, separator, *lines])


class WarehouseService:
    """Coordinates warehouse use cases using dependency injection."""

    def __init__(
        self,
        warehouse: Warehouse,
        reorder_policy: ReorderPolicy,
        report_service: ReportService,
    ) -> None:
        self._warehouse = warehouse
        self._reorder_policy = reorder_policy
        self._report_service = report_service

    def search(self, code: str) -> WarehouseItem | None:
        """Find an inventory item by its product code."""
        return self._warehouse.find_by_code(code)

    def apply_operation(
        self,
        payload: StockOperationPayload,
    ) -> StockOperationResult:
        """Apply a receipt or write-off operation."""
        operation_name = payload["operation"].lower()

        if operation_name == "receipt":
            operation: StockOperation = ReceiptOperation(
                payload["operation_id"],
                payload["code"],
                payload["quantity"],
            )
        elif operation_name == "write_off":
            operation = WriteOffOperation(
                payload["operation_id"],
                payload["code"],
                payload["quantity"],
            )
        else:
            raise ValueError(
                "Тип операції має бути receipt або write_off"
            )

        return operation.execute(self._warehouse)

    def low_stock(self) -> list[WarehouseItem]:
        """Return items that require replenishment."""
        return [
            item
            for item in self._warehouse
            if self._reorder_policy.should_reorder(item)
        ]

    def reorder_suggestions(self) -> list[str]:
        """Build replenishment suggestions for low-stock items."""
        return [
            f"{item.product.code}: замовити "
            f"{self._reorder_policy.recommended_quantity(item)} од."
            for item in self._warehouse
            if self._reorder_policy.should_reorder(item)
        ]

    def inventory_report(self) -> str:
        """Generate a report containing items and total inventory value."""
        lines = [
            str(item)
            + f"; ціна={item.product.price}; сума={item.total_value}"
            for item in self._warehouse
        ]
        lines.append(
            f"Загальна вартість: {self._warehouse.total_value}"
        )
        return self._report_service.render(
            "Звіт складських запасів",
            lines,
        )