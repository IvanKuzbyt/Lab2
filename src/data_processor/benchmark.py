
from timeit import repeat
from typing import Any

from .processors import create_inventory_index, find_product_by_code


def run_benchmark() -> list[tuple[int, float, float]]:
    results: list[tuple[int, float, float]] = []

    for size in (1_000, 10_000, 100_000):
        items: list[dict[str, Any]] = [
            {
                "code": f"P{i:06}",
                "name": f"Товар {i}",
                "category": "Тест",
                "quantity": i % 50,
                "price": float(i),
            }
            for i in range(size)
        ]

        target: str = items[-1]["code"]
        index = create_inventory_index(items)

        list_time = min(
            repeat(
                lambda: find_product_by_code(items, target),
                number=100,
                repeat=5,
            )
        ) / 100

        dict_time = min(
            repeat(
                lambda: index.get(target),
                number=100,
                repeat=5,
            )
        ) / 100

        results.append((size, list_time, dict_time))

    return results


if __name__ == "__main__":
    for size, list_time, dict_time in run_benchmark():
        print(f"{size:>7} | {list_time:.8f} | {dict_time:.8f}")