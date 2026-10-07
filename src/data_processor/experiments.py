from __future__ import annotations

import gc
import time
import tracemalloc
from pathlib import Path
from collections.abc import Callable

from .analytics import calculate_total_value
from .pipeline import build_pipeline


def eager_total(path: Path) -> float:
    records = list(build_pipeline(path))
    return calculate_total_value(records)


def lazy_total(path: Path) -> float:
    return calculate_total_value(build_pipeline(path))


def measure(
    function: Callable[[Path], float],
    path: Path,
) -> tuple[float, float, float]:
    gc.collect()
    tracemalloc.start()
    started = time.perf_counter()

    result = function(path)

    elapsed = time.perf_counter() - started
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return result, elapsed, peak / (1024 * 1024)


def run_eager_lazy_experiment(path: Path) -> dict[str, tuple[float, float]]:
    eager_result, eager_time, eager_memory = measure(eager_total, path)
    lazy_result, lazy_time, lazy_memory = measure(lazy_total, path)
    if abs(eager_result - lazy_result) > 0.01:
        raise RuntimeError("Eager and lazy results differ")
    return {
        "eager": (eager_time, eager_memory),
        "lazy": (lazy_time, lazy_memory),
    }
