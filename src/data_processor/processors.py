from collections import Counter, defaultdict
from collections.abc import Callable
from typing import Any

def get_unique_categories(items: list[dict[str, Any]]) -> set[str]:
    return {item["category"] for item in items}

def create_inventory_index(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {item["code"]: item for item in items}

def find_product_by_code(items: list[dict[str, Any]], code: str) -> dict[str, Any] | None:
    for item in items:
        if item["code"].casefold() == code.casefold():
            return item
    return None

def find_in_index(index: dict[str, dict[str, Any]], code: str) -> dict[str, Any] | None:
    return index.get(code.upper())

def get_low_stock_items(items: list[dict[str, Any]], threshold: int = 5) -> list[dict[str, Any]]:
    return [item for item in items if item["quantity"] <= threshold]

def group_by_category(items: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped = defaultdict(list)
    for item in items:
        grouped[item["category"]].append(item)
    return dict(grouped)

def count_products_by_category(
    items: list[dict[str, Any]],
) -> Counter[str]:
    return Counter(item["category"] for item in items)

def filter_items(items: list[dict[str, Any]], predicate: Callable[[dict[str, Any]], bool]) -> list[dict[str, Any]]:
    return [item for item in items if predicate(item)]

def filter_by_category(items: list[dict[str, Any]], category: str) -> list[dict[str, Any]]:
    return filter_items(items, lambda item: item["category"] == category)

def sort_by_price(items: list[dict[str, Any]], reverse: bool = True) -> list[dict[str, Any]]:
    return sorted(items, key=lambda item: item["price"], reverse=reverse)
