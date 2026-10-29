import json
import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from collections.abc import Iterator, Iterable
from typing import Any, TextIO, cast
from .exceptions import DataExportError


@contextmanager
def atomic_output(path: Path) -> Iterator[TextIO]:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, prefix=path.name + ".", suffix=".tmp", delete=False
        ) as file:
            temp = Path(file.name)
            yield cast(TextIO, file)
            file.flush()
            os.fsync(file.fileno())
        os.replace(temp, path)
    except Exception:
        if temp is not None:
            temp.unlink(missing_ok=True)
        raise


def export_json(records: Iterable[Any], path: Path) -> None:
    try:
        with atomic_output(path) as file:
            file.write("[\n")
            first = True
            for item in records:
                if not first:
                    file.write(",\n")
                json.dump(
                    {
                        "code": item.code,
                        "name": item.name,
                        "quantity": item.quantity,
                        "price": item.price,
                        "category": item.category,
                    },
                    file,
                    ensure_ascii=False,
                )
                first = False
            file.write("\n]\n")
    except (OSError, TypeError, ValueError) as error:
        raise DataExportError(f"Cannot export to {path}") from error
