# Lab 9 — Warehouse performance (variant 10)

Extends Labs 1–8. Existing SQLite/ORM/FastAPI remain unchanged. New analytics operate on immutable snapshots, not on shared SQLAlchemy sessions.

## Setup (Windows PowerShell)
```powershell
python -m pip install -e ".[dev]"
python -m pytest -v
python -m benchmarks.benchmark_lab9 --size 100000 --repeats 5
```

Results are generated under `benchmarks/results/benchmark_results.csv` and `cprofile.txt`.
For faster verification: `python -m benchmarks.benchmark_lab9 --size 10000 --repeats 3 --workers 1 2`.

## Experiments
- CPU-bound stock valuation and low-stock statistics: baseline, NumPy, threads, processes; equality checked.
- I/O-bound: `load_journals_sequential` vs `load_journals_threads` for CSV logs.
- Explicit `thread_example`, `process_example`, and lost-update race demonstration corrected with `Lock`.
- `cProfile` bottleneck report; `tracemalloc` peak memory; versioned `lru_cache` invalidated after stock movement.
- Worker scaling: 1, 2, 4, 8; repeated timing and speedup relative to the equivalent Python baseline.

Note: thread/process timings are compared against Python total-only baseline; NumPy and cache timings against full Python statistics baseline. This prevents comparing different workloads. Results depend on machine and Python version. Multiprocessing requires the `if __name__ == "__main__"` entry point on Windows.
