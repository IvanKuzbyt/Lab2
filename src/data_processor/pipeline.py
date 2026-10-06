from collections.abc import Iterator
from pathlib import Path

from .filters import filter_low_stock, validate_inventory
from .models import InventoryRecord
from .parsers import parse_inventory
from .readers import read_csv_rows
from .transformations import normalize_records


def build_pipeline(path: Path) -> Iterator[InventoryRecord]:
    rows = read_csv_rows(path)
    parsed = parse_inventory(rows)
    valid = validate_inventory(parsed)
    normalized = normalize_records(valid)
    yield from normalized


def build_low_stock_pipeline(path: Path, threshold: int = 5) -> Iterator[InventoryRecord]:
    records = build_pipeline(path)
    yield from filter_low_stock(records, threshold)
