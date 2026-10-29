"""Thread/process experiments; do not share SQLAlchemy sessions across workers."""

from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from multiprocessing import Process, Queue
from threading import Thread, Lock
import csv
from .analytics import total_value_python


def _chunk_total(chunk):
    return total_value_python(chunk)


def _chunks(items, workers):
    step = max(1, (len(items) + workers - 1) // workers)
    return [items[i : i + step] for i in range(0, len(items), step)]


def total_value_threads(items, workers=4):
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return sum(pool.map(_chunk_total, _chunks(items, workers)))


def total_value_processes(items, workers=4):
    with ProcessPoolExecutor(max_workers=workers) as pool:
        return sum(pool.map(_chunk_total, _chunks(items, workers)))


def _read_journal(path):
    with open(path, newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def load_journals_sequential(paths):
    return [record for path in paths for record in _read_journal(path)]


def load_journals_threads(paths, workers=4):
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return [record for records in pool.map(_read_journal, paths) for record in records]


def thread_example(values):
    output = [None] * len(values)

    def worker(i, value):
        output[i] = value * value

    threads = [Thread(target=worker, args=(i, v)) for i, v in enumerate(values)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    return output


def _process_square(value, queue):
    queue.put(value * value)


def process_example(value):
    queue: Queue[int] = Queue()
    process = Process(target=_process_square, args=(value, queue))
    process.start()
    result = queue.get(timeout=10)
    process.join(timeout=10)
    if process.exitcode != 0:
        raise RuntimeError("child process failed")
    return result


def concurrent_stock_updates(initial=100, workers=8, iterations=1000):
    """Demonstrate a correct shared in-memory update protected by Lock."""
    stock = [initial]
    lock = Lock()

    def update():
        for _ in range(iterations):
            with lock:
                stock[0] += 1

    threads = [Thread(target=update) for _ in range(workers)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    return stock[0]


def race_condition_demo(workers=8, iterations=100):
    """Force a lost update by splitting read/write; demonstration only."""
    from threading import Barrier

    stock = [0]
    barrier = Barrier(workers)

    def unsafe():
        for _ in range(iterations):
            old = stock[0]
            barrier.wait()
            stock[0] = old + 1
            barrier.wait()

    threads = [Thread(target=unsafe) for _ in range(workers)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    return stock[0]
