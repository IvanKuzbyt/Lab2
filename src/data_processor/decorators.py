from functools import wraps
from time import perf_counter
from collections.abc import Callable
from typing import Any

def measure_time(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = perf_counter()
        result = func(*args, **kwargs)
        elapsed = perf_counter() - start
        print(f"[Час] {func.__name__}: {elapsed:.8f} с")
        return result
    return wrapper
