from collections.abc import Iterable, Iterator

from .models import InventoryRecord


def validate_inventory(records: Iterable[InventoryRecord]) -> Iterator[InventoryRecord]:
    for record in records:
        if not record.code or not record.name or not record.category:
            continue
        if record.quantity < 0 or record.price <= 0:
            continue
        yield record


def filter_low_stock(records: Iterable[InventoryRecord], threshold: int = 5) -> Iterator[InventoryRecord]:
    for record in records:
        if record.quantity <= threshold:
            yield record


def filter_by_category(records: Iterable[InventoryRecord], category: str) -> Iterator[InventoryRecord]:
    for record in records:
        if record.category == category:
            yield record
