"""CPU and memory profiling of actual warehouse analytics."""

from __future__ import annotations
import cProfile
import io
import pstats
import tracemalloc
from .analytics import statistics_python


def profile_catalog(items, top=12):
    profiler = cProfile.Profile()
    profiler.enable()
    result = statistics_python(items)
    profiler.disable()
    output = io.StringIO()
    pstats.Stats(profiler, stream=output).sort_stats("cumulative").print_stats(top)
    return result, output.getvalue()


def memory_profile(items):
    tracemalloc.start()
    try:
        result = statistics_python(items)
        current, peak = tracemalloc.get_traced_memory()
        return result, current / (1024 * 1024), peak / (1024 * 1024)
    finally:
        tracemalloc.stop()
