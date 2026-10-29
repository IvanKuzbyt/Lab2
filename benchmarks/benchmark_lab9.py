"""Run: python -m benchmarks.benchmark_lab9 --size 100000 --repeats 5"""

from __future__ import annotations
import argparse
import csv
import math
import platform
from pathlib import Path
from statistics import mean
from time import perf_counter
from warehouse_persistence.analytics import (
    generate_catalog,
    statistics_python,
    statistics_numpy,
    WarehouseStatisticsCache,
    total_value_python,
)
from warehouse_persistence.parallel import (
    total_value_threads,
    total_value_processes,
    race_condition_demo,
    concurrent_stock_updates,
)
from warehouse_persistence.profiling import profile_catalog, memory_profile


def measure(fn, repeats):
    times = []
    for _ in range(repeats):
        start = perf_counter()
        fn()
        times.append(perf_counter() - start)
    return mean(times)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", type=int, default=100_000)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--workers", type=int, nargs="+", default=[1, 2, 4, 8])
    args = parser.parse_args()
    if args.repeats < 2 or args.size < 1:
        parser.error("size >= 1 and repeats >= 2 required")
    catalog = generate_catalog(args.size)
    baseline = statistics_python(catalog)
    vector = statistics_numpy(catalog)
    for key in baseline:
        assert math.isclose(baseline[key], vector[key], rel_tol=1e-9, abs_tol=1e-7), key
    _, profile = profile_catalog(catalog)
    _, current, peak = memory_profile(catalog)
    out = Path("benchmarks/results")
    out.mkdir(parents=True, exist_ok=True)
    (out / "cprofile.txt").write_text(profile, encoding="utf-8")
    rows = []

    def add(name, fn, workers="-", memory=""):
        value = fn()
        if isinstance(value, dict):
            value = value["total_value"]
        assert math.isclose(value, baseline["total_value"], rel_tol=1e-9, abs_tol=1e-5), name
        elapsed = measure(fn, args.repeats)
        rows.append(
            {
                "method": name,
                "data_size": args.size,
                "workers": workers,
                "mean_seconds": f"{elapsed:.8f}",
                "peak_memory_mb": memory,
                "speedup": "",
                "python": platform.python_version(),
            }
        )

    add("Python baseline total", lambda: total_value_python(catalog), 1)
    add("Python full statistics", lambda: statistics_python(catalog), 1, f"{peak:.3f}")
    add("NumPy vectorized", lambda: statistics_numpy(catalog), 1)
    for workers in args.workers:
        add("ThreadPoolExecutor", lambda w=workers: total_value_threads(catalog, w), workers)
        add("ProcessPoolExecutor", lambda w=workers: total_value_processes(catalog, w), workers)
    cache = WarehouseStatisticsCache(lambda: catalog)
    cache.statistics()
    add("Cached warm", cache.statistics, 1)
    total_base = float(rows[0]["mean_seconds"])
    stats_base = float(rows[1]["mean_seconds"])
    for row in rows:
        base = (
            stats_base if row["method"] in ("Python full statistics", "NumPy vectorized", "Cached warm") else total_base
        )
        row["speedup"] = f"{base / float(row['mean_seconds']):.3f}"
    with (out / "benchmark_results.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print("Method                    Workers     Mean(s)    Speedup")
    for row in rows:
        print(f"{row['method']:26} {str(row['workers']):>5} {row['mean_seconds']:>12} {row['speedup']:>9}x")
    print(f"Python tracemalloc current={current:.3f} MB peak={peak:.3f} MB")
    print(
        "Race condition:",
        race_condition_demo(),
        "(expected with Lock:",
        concurrent_stock_updates(initial=0, workers=8, iterations=100),
        ")",
    )
    print("Saved:", out / "benchmark_results.csv", out / "cprofile.txt")


if __name__ == "__main__":
    main()
