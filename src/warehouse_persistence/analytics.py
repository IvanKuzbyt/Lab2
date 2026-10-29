"""Pure analytics over a warehouse catalog; no database state is cached."""

from __future__ import annotations
from collections import defaultdict
from functools import lru_cache
import math
import random


def generate_catalog(count: int = 100_000, seed: int = 42) -> list[tuple[int, float, int]]:
    if count < 1:
        raise ValueError("count must be positive")
    rng = random.Random(seed)
    return [(rng.randint(0, 200), round(rng.uniform(1, 2000), 2), rng.randint(2, 30)) for _ in range(count)]


def total_value_python(items):
    result = 0.0
    for quantity, price, _ in items:
        result += quantity * price
    return result


def low_stock_python(items):
    return sum(1 for quantity, _, minimum in items if quantity < minimum)


def statistics_python(items):
    n = len(items)
    if not n:
        raise ValueError("empty catalog")
    values = [q * price for q, price, _ in items]
    avg = sum(values) / n
    variance = sum((x - avg) ** 2 for x in values) / n
    return {
        "total_value": sum(values),
        "mean_value": avg,
        "minimum_value": min(values),
        "maximum_value": max(values),
        "std_value": math.sqrt(variance),
        "low_stock_count": low_stock_python(items),
    }


def statistics_numpy(items):
    import numpy as np

    array = np.asarray(items, dtype=np.float64)
    if not len(array):
        raise ValueError("empty catalog")
    values = array[:, 0] * array[:, 1]
    return {
        "total_value": float(values.sum()),
        "mean_value": float(values.mean()),
        "minimum_value": float(values.min()),
        "maximum_value": float(values.max()),
        "std_value": float(values.std()),
        "low_stock_count": int(np.count_nonzero(array[:, 0] < array[:, 2])),
    }


def operation_statistics(operations):
    """Operations: (product_code, kind, quantity)."""
    totals: defaultdict[str, dict[str, int]] = defaultdict(lambda: {"receipt": 0, "write_off": 0})
    for code, kind, amount in operations:
        if kind not in ("receipt", "write_off"):
            raise ValueError("unknown operation")
        totals[code][kind] += amount
    return dict(totals)


class WarehouseStatisticsCache:
    """Versioned cache; call record_movement after every successful stock movement."""

    def __init__(self, supplier):
        self.supplier = supplier
        self.version = 0
        self._compute = lru_cache(maxsize=16)(self._calculate)

    def _calculate(self, version):
        return statistics_python(self.supplier())

    def statistics(self):
        return self._compute(self.version).copy()

    def record_movement(self):
        self.version += 1
        self._compute.cache_clear()

    def cache_info(self):
        return self._compute.cache_info()
