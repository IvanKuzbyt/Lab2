from pathlib import Path

from data_processor.analytics import apply_operations, count_valid_invalid, find_min_max_price, streaming_average_price
from data_processor.batches import batched
from data_processor.filters import filter_low_stock
from data_processor.iterators import InventoryCodeIterator
from data_processor.pipeline import build_pipeline
from data_processor.readers import read_csv_rows


def test_pipeline_validates_records() -> None:
    path = Path("data/demo_inventory.csv")
    records = list(build_pipeline(path))
    assert [record.code for record in records] == ["A001", "A002", "A003", "D001"]


def test_low_stock_filter() -> None:
    path = Path("data/demo_inventory.csv")
    records = list(filter_low_stock(build_pipeline(path), 4))
    assert [record.code for record in records] == ["A001", "A003", "D001"]


def test_streaming_analytics() -> None:
    path = Path("data/demo_inventory.csv")
    records = build_pipeline(path)
    minimum, maximum = find_min_max_price(records)
    assert minimum == 799
    assert maximum == 34999
    assert round(streaming_average_price(build_pipeline(path)), 2) == 16824.0


def test_batches() -> None:
    assert list(batched(range(7), 3)) == [[0, 1, 2], [3, 4, 5], [6]]


def test_iterator_protocol() -> None:
    iterator = InventoryCodeIterator(["A", "B"])
    assert iter(iterator) is iterator
    assert next(iterator) == "A"
    assert next(iterator) == "B"


def test_valid_invalid_count() -> None:
    rows = read_csv_rows(Path("data/demo_inventory.csv"))
    assert count_valid_invalid(rows) == (4, 1)


def test_operations_do_not_allow_negative_stock() -> None:
    records = build_pipeline(Path("data/demo_inventory.csv"))
    operations = [
        {"code": "A001", "operation": "issue", "quantity": 100},
        {"code": "A001", "operation": "receipt", "quantity": 5},
    ]
    stock = apply_operations(records, operations)
    assert stock["A001"] == 9
