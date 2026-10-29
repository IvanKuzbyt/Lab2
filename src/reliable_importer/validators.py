from decimal import Decimal, InvalidOperation
from data_processor.models import InventoryRecord
from .exceptions import RecordValidationError


def validate(row: dict[str, str | None], line: int) -> InventoryRecord:
    for field in ("code", "name", "quantity", "price", "category"):
        if not row.get(field) or not str(row[field]).strip():
            raise RecordValidationError(f"Missing {field}", line_number=line, field=field)
    try:
        quantity = int(str(row["quantity"]))
        price = Decimal(str(row["price"]))
    except (ValueError, InvalidOperation) as error:
        raise RecordValidationError("Invalid quantity or price", line_number=line, field="quantity/price") from error
    if quantity < 0 or not price.is_finite() or price < 0:
        raise RecordValidationError("Negative quantity or invalid price", line_number=line)
    return InventoryRecord(
        str(row["code"]).strip(), str(row["name"]).strip(), quantity, float(price), str(row["category"]).strip()
    )
