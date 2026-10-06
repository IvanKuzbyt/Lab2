from collections.abc import Iterable, Iterator

from .models import InventoryRecord


def normalize_records(records: Iterable[InventoryRecord]) -> Iterator[InventoryRecord]:
    for record in records:
        yield InventoryRecord(
            code=record.code.upper(),
            name=record.name.strip(),
            quantity=record.quantity,
            price=round(record.price, 2),
            category=record.category.strip(),
        )


def compact_view(records: Iterable[InventoryRecord]) -> Iterator[str]:
    for record in records:
        yield f"{record.code}: {record.name} ({record.quantity} од.)"
