from dataclasses import FrozenInstanceError
from decimal import Decimal

import pytest

from warehouse_manager.dto import StockOperationPayload
from warehouse_manager.main import build_demo_service
from warehouse_manager.models import Product, Supplier, Warehouse, WarehouseItem
from warehouse_manager.operations import ReceiptOperation, WriteOffOperation
from warehouse_manager.repositories import InMemoryRepository
from warehouse_manager.services import ThresholdReorderPolicy
from warehouse_manager.value_objects import Money


def sample_item(quantity: int = 4) -> WarehouseItem:
    supplier = Supplier(1, "Постачальник", "supplier@example.com")
    product = Product(1, "A001", "Тестовий товар", "Тести", Money(Decimal("10")), supplier)
    return WarehouseItem(1, product, quantity, 5)


def test_money_is_immutable_and_supports_arithmetic() -> None:
    money = Money(Decimal("10"))
    assert str(money + Money(Decimal("2.5"))) == "12.50 UAH"
    assert str(money * 3) == "30.00 UAH"
    with pytest.raises(FrozenInstanceError):
        money.currency = "USD"  # type: ignore[misc]


def test_property_and_stock_encapsulation() -> None:
    item = sample_item(4)
    assert item.is_low_stock
    assert str(item.total_value) == "40.00 UAH"
    item.receive(3)
    assert item.quantity == 7
    item.write_off(2)
    assert item.quantity == 5
    with pytest.raises(ValueError):
        item.write_off(6)


def test_warehouse_search_total_and_dunder_methods() -> None:
    warehouse = Warehouse(1, "Тестовий склад")
    item = sample_item(4)
    warehouse.add_item(item)
    assert len(warehouse) == 1
    assert "a001" in warehouse
    assert list(warehouse) == [item]
    assert warehouse.find_by_code("A001") is item
    assert str(warehouse.total_value) == "40.00 UAH"


def test_receipt_and_write_off_polymorphism() -> None:
    warehouse = Warehouse(1, "Тестовий склад")
    warehouse.add_item(sample_item(4))
    receipt = ReceiptOperation(1, "A001", 5).execute(warehouse)
    assert receipt.quantity_after == 9
    write_off = WriteOffOperation(2, "A001", 3).execute(warehouse)
    assert write_off.quantity_after == 6


def test_service_uses_injected_reorder_and_report_services() -> None:
    service = build_demo_service()
    assert service.search("a002") is not None
    assert service.search("missing") is None
    assert service.low_stock()
    assert "Звіт складських запасів" in service.inventory_report()


def test_typed_dict_operation_payload() -> None:
    service = build_demo_service()
    payload: StockOperationPayload = {
        "operation_id": 50, "code": "A001", "operation": "receipt", "quantity": 2,
    }
    result = service.apply_operation(payload)
    assert result.quantity_after == 6


def test_reorder_policy_and_invalid_inputs() -> None:
    policy = ThresholdReorderPolicy(threshold=5, target_quantity=20)
    item = sample_item(3)
    assert policy.should_reorder(item)
    assert policy.recommended_quantity(item) == 17
    with pytest.raises(ValueError):
        Money(Decimal("-1"))
    with pytest.raises(ValueError):
        item.receive(0)
    with pytest.raises(ValueError):
        ThresholdReorderPolicy(threshold=10, target_quantity=5)


def test_generic_repository() -> None:
    repository: InMemoryRepository[Product] = InMemoryRepository()
    supplier = Supplier(1, "Постачальник", "supplier@example.com")
    product = Product(1, "A001", "Тест", "Тести", Money(Decimal("1")), supplier)
    repository.add(product)
    assert repository.get(1) is product
    assert repository.all() == [product]
    assert repository.remove(1)
    assert len(repository) == 0


def test_oop_service_can_be_built_from_lab3_streaming_pipeline() -> None:
    from itertools import islice
    from pathlib import Path
    from data_processor.pipeline import build_pipeline
    from warehouse_manager.main import build_service_from_records

    records = islice(build_pipeline(Path("data/inventory.csv")), 10)
    service = build_service_from_records(records)
    assert len(service.low_stock()) >= 0
    assert service.search("INV000010") is not None
    assert service.search("NOT-FOUND") is None
