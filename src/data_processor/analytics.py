from collections import Counter
from collections.abc import Iterable

from .models import InventoryRecord


def calculate_total_value(products):
    """Обчислює загальну вартість усіх товарів на складі."""
    return sum(
        product.quantity * product.price
        for product in products
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

def find_most_expensive(products):
    """Повертає товар із найвищою ціною."""
    return max(products, key=lambda product: product["price"])


def create_stock_filter(min_quantity):
    """Створює функцію для фільтрації товарів за залишком."""
    return lambda product: product["quantity"] <= min_quantity


