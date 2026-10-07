"""Small structural interfaces used by application services."""

from typing import Protocol, runtime_checkable

from warehouse_manager.models import WarehouseItem


@runtime_checkable
class ReorderPolicy(Protocol):
    def should_reorder(self, item: WarehouseItem) -> bool: ...
    def recommended_quantity(self, item: WarehouseItem) -> int: ...


class ReportService(Protocol):
    def render(self, title: str, lines: list[str]) -> str: ...
