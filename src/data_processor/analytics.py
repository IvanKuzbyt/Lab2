from collections.abc import Callable
from typing import Any
from .decorators import measure_time

@measure_time
def calculate_total_value(items: list[dict[str, Any]]) -> float:
    return sum(item["quantity"] * item["price"] for item in items)

def find_most_expensive(items: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not items:
        return None
    return max(items, key=lambda item: item["price"])

def calculate_average(*values: float) -> float:
    return sum(values) / len(values) if values else 0.0

def create_product(**fields: Any) -> dict[str, Any]:
    return dict(fields)

def create_stock_filter(min_quantity: int) -> Callable[[dict[str, Any]], bool]:
    def predicate(item: dict[str, Any]) -> bool:
        return item["quantity"] <= min_quantity
    return predicate
