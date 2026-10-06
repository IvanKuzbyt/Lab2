from collections.abc import Iterable, Iterator

from .models import InventoryRecord, StockOperation


def parse_inventory(rows: Iterable[dict[str, str]]) -> Iterator[InventoryRecord]:
    for row in rows:
        try:
            yield InventoryRecord(
                code=row["code"].strip(),
                name=row["name"].strip(),
                quantity=int(row["quantity"]),
                price=float(row["price"]),
                category=row["category"].strip(),
            )
        except (KeyError, TypeError, ValueError):
            continue


def parse_operations(rows: Iterable[dict[str, str]]) -> Iterator[StockOperation]:
    for row in rows:
        try:
            yield StockOperation(
                code=row["code"].strip(),
                operation=row["operation"].strip().lower(),
                quantity=int(row["quantity"]),
            )
        except (KeyError, TypeError, ValueError):
            continue
