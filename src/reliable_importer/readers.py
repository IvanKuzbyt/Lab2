import csv
from pathlib import Path
from collections.abc import Iterator
from .exceptions import DataImportError

def read_rows(path: Path) -> Iterator[tuple[int, dict[str, str | None]]]:
    try:
        with path.open(encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)
            expected = {"code", "name", "quantity", "price", "category"}
            if not reader.fieldnames or not expected.issubset(reader.fieldnames):
                raise DataImportError("CSV header missing required columns")
            for line, row in enumerate(reader, 2):
                yield line, row
    except (OSError, UnicodeError, csv.Error) as error:
        raise DataImportError(f"Cannot read {path}") from error
