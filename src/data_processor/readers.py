from collections.abc import Iterator
from pathlib import Path


def read_lines(path: Path) -> Iterator[str]:
    """Read a text file lazily, one line at a time."""
    with path.open("r", encoding="utf-8", newline="") as file:
        yield from file


def read_csv_rows(path: Path) -> Iterator[dict[str, str]]:
    """Stream CSV rows without loading the complete file."""
    import csv

    lines = read_lines(path)
    reader = csv.DictReader(lines)
    yield from reader
