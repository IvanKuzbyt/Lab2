from collections import Counter
from collections.abc import Callable, Iterable
from typing import Any

from .models import InventoryRecord


def calculate_total_value(records: Iterable[InventoryRecord]) -> float:
    return sum(
        (record["quantity"] if isinstance(record, dict) else record.quantity)
        * (record["price"] if isinstance(record, dict) else record.price)
        for record in records
    )


def streaming_average_price(records: Iterable[InventoryRecord]) -> float:
    total = 0.0
    count = 0
    for record in records:
        total += record.price
        count += 1
    return total / count if count else 0.0


def find_min_max_price(records: Iterable[InventoryRecord]) -> tuple[float | None, float | None]:
    minimum = maximum = None
    for record in records:
        if minimum is None or record.price < minimum:
            minimum = record.price
        if maximum is None or record.price > maximum:
            maximum = record.price
    return minimum, maximum


def count_categories(records: Iterable[InventoryRecord]) -> Counter[str]:
    return Counter(record.category for record in records)


def count_valid_invalid(rows: Iterable[dict[str, str]]) -> tuple[int, int]:
    valid = invalid = 0
    for row in rows:
        try:
            code = row["code"].strip()
            name = row["name"].strip()
            category = row["category"].strip()
            quantity = int(row["quantity"])
            price = float(row["price"])
            if not code or not name or not category or quantity < 0 or price <= 0:
                raise ValueError
            valid += 1
        except (KeyError, TypeError, ValueError):
            invalid += 1
    return valid, invalid


def apply_operations(records: Iterable[InventoryRecord], operations: Iterable[dict[str, str]]) -> dict[str, int]:
    stock = {record.code: record.quantity for record in records}
    for row in operations:
        try:
            code = row["code"].strip().upper()
            operation = row["operation"].strip().lower()
            quantity = int(row["quantity"])
            if quantity < 0 or code not in stock or operation not in {"receipt", "issue"}:
                continue
            if operation == "receipt":
                stock[code] += quantity
            elif stock[code] >= quantity:
                stock[code] -= quantity
        except (KeyError, TypeError, ValueError):
            continue
    return stock

def find_most_expensive(
    records: Iterable[InventoryRecord | dict[str, Any]],
) -> InventoryRecord | dict[str, Any] | None:
    most_expensive: InventoryRecord | dict[str, Any] | None = None

    for record in records:
        price = record["price"] if isinstance(record, dict) else record.price

        if most_expensive is None:
            most_expensive = record
            continue

        max_price = (
            most_expensive["price"]
            if isinstance(most_expensive, dict)
            else most_expensive.price
        )

        if price > max_price:
            most_expensive = record

    return most_expensive


def create_stock_filter(
    max_quantity: int,
) -> Callable[[InventoryRecord | dict[str, Any]], bool]:
    def stock_filter(record: InventoryRecord | dict[str, Any]) -> bool:
        quantity = (
            record["quantity"]
            if isinstance(record, dict)
            else record.quantity
        )
        return quantity <= max_quantity

    return stock_filter
