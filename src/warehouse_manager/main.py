"""Entry point integrating Lab 3 streaming pipeline and Lab 4 OOP model."""

from decimal import Decimal
from itertools import islice
from pathlib import Path
from typing import Iterable

from data_processor.analytics import calculate_total_value, count_valid_invalid, find_min_max_price
from data_processor.models import InventoryRecord
from data_processor.pipeline import build_pipeline
from data_processor.readers import read_csv_rows

from warehouse_manager.dto import StockOperationPayload
from warehouse_manager.models import Product, Supplier, Warehouse, WarehouseItem
from warehouse_manager.repositories import InMemoryRepository
from warehouse_manager.services import ConsoleReportService, ThresholdReorderPolicy, WarehouseService
from warehouse_manager.value_objects import Money

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"


def build_service_from_records(records: Iterable[InventoryRecord]) -> WarehouseService:
    """Build OOP domain objects from the existing Lab 3 streaming records."""
    supplier = Supplier(1, "Постачальник із каталогу ЛР3", "catalog@example.com")
    warehouse = Warehouse(1, "Основний склад")
    product_repository: InMemoryRepository[Product] = InMemoryRepository()
    for index, record in enumerate(records, start=1):
        product = Product(
            id=index,
            code=record.code,
            name=record.name,
            category=record.category,
            _price=Money(Decimal(str(record.price))),
            supplier=supplier,
        )
        product_repository.add(product)
        warehouse.add_item(WarehouseItem(index, product, record.quantity, low_stock_threshold=5))
    return WarehouseService(warehouse, ThresholdReorderPolicy(), ConsoleReportService())


def build_demo_service() -> WarehouseService:
    """Small fallback demo used by isolated OOP unit tests."""
    from data_processor.models import InventoryRecord
    demo_path = DATA / "demo_inventory.csv"
    records = list(islice(build_pipeline(demo_path), 4))
    return build_service_from_records(records)


def main() -> None:
    inventory_path = DATA / "inventory.csv"
    operations_path = DATA / "operations.csv"
    print("=== ЛАБОРАТОРНА РОБОТА №4: ООП ДЛЯ СИСТЕМИ СКЛАДСЬКОГО ОБЛІКУ ===")
    print("Основа — проєкт ЛР3: потокова обробка CSV, генератори та lazy pipeline")

    valid, invalid = count_valid_invalid(read_csv_rows(inventory_path))
    total = calculate_total_value(build_pipeline(inventory_path))
    minimum, maximum = find_min_max_price(build_pipeline(inventory_path))
    print("\nПотокова статистика всього набору inventory.csv:")
    print(f"Валідних записів: {valid}; невалідних: {invalid}")
    print(f"Загальна вартість: {total:,.2f} грн")
    print(f"Мінімальна ціна: {minimum:.2f} грн; максимальна ціна: {maximum:.2f} грн")

    # The domain collection demonstrates OOP behavior on a bounded sample;
    # the full dataset remains processed lazily by data_processor.
    sample_records = list(islice(build_pipeline(inventory_path), 10))
    service = build_service_from_records(sample_records)
    print("\nООП-модель складу (перші 10 валідних позицій із потоку):")
    print(service.inventory_report())
    print("\nПошук INV000010:", service.search("inv000010"))

    operation_rows = read_csv_rows(operations_path)
    print("\nОбробка перших операцій із data/operations.csv:")
    for operation_id, row in enumerate(islice(operation_rows, 6), start=1):
        try:
            operation_name = row["operation"].strip().lower()
            payload: StockOperationPayload = {
                "operation_id": operation_id,
                "code": row["code"].strip(),
                "operation": "receipt" if operation_name == "receipt" else "write_off",
                "quantity": int(row["quantity"]),
            }
            print(service.apply_operation(payload))
        except (KeyError, TypeError, ValueError) as error:
            print(f"Операцію {row.get('operation', '?')} для {row.get('code', '?')} відхилено: {error}")

    print("\nПозиції, що потребують поповнення:")
    suggestions = service.reorder_suggestions()
    for suggestion in suggestions[:10]:
        print("-", suggestion)
    if not suggestions:
        print("Немає позицій нижче порога поповнення.")


if __name__ == "__main__":
    main()
