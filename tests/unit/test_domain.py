from decimal import Decimal
from unittest.mock import Mock
import pytest
from warehouse_manager.models import Supplier, Product, WarehouseItem, Warehouse
from warehouse_manager.value_objects import Money
from warehouse_manager.services import ThresholdReorderPolicy, WarehouseService, ConsoleReportService
from warehouse_manager.operations import ReceiptOperation, WriteOffOperation

@pytest.mark.parametrize("quantity", [0, 1, 5, 100])
def test_receive_valid(item, quantity):
    original = item.quantity
    if quantity == 0:
        with pytest.raises(ValueError): item.receive(quantity)
    else:
        item.receive(quantity)
        assert item.quantity == original + quantity

@pytest.mark.parametrize("quantity", [-1, 0, 4, 100])
def test_write_off_invalid(item, quantity):
    with pytest.raises(ValueError): item.write_off(quantity)
    assert item.quantity == 3

def test_write_off_success(item):
    item.write_off(3)
    assert item.quantity == 0

def test_money_precision():
    assert float(Money(Decimal("0.105")).amount) == pytest.approx(0.10)

def test_money_reject_negative():
    with pytest.raises(ValueError): Money(Decimal("-1"))

def test_money_reject_currency():
    with pytest.raises(ValueError): Money(Decimal("1"), "LONG")

def test_supplier_validation():
    with pytest.raises(ValueError): Supplier(0, "", "invalid")

def test_product_validation(item):
    with pytest.raises(ValueError): Product(0, "", "", "", item.product.price, item.product.supplier)

def test_item_invalid_quantity(item):
    with pytest.raises(ValueError): WarehouseItem(5, item.product, -1)

def test_search_case_insensitive(warehouse):
    assert warehouse.find_by_code("sku-1") is warehouse.find_by_code("SKU-1")

def test_search_missing(warehouse):
    assert warehouse.find_by_code("MISSING") is None

def test_duplicate_item(warehouse, item):
    with pytest.raises(ValueError): warehouse.add_item(item)

def test_total_value(warehouse):
    assert float(warehouse.total_value.amount) == pytest.approx(37.5)

def test_low_stock(warehouse, item):
    assert warehouse.low_stock_items() == [item]

def test_reorder_policy(item):
    policy = ThresholdReorderPolicy(5, 20)
    assert policy.should_reorder(item)
    assert policy.recommended_quantity(item) == 17

def test_reorder_policy_invalid():
    with pytest.raises(ValueError): ThresholdReorderPolicy(10, 10)

def test_receipt_operation(warehouse, item):
    result = ReceiptOperation(1, "SKU-1", 4).execute(warehouse)
    assert result.quantity_after == 7
    assert item.quantity == 7

def test_writeoff_operation(warehouse, item):
    result = WriteOffOperation(2, "SKU-1", 2).execute(warehouse)
    assert result.quantity_after == 1

def test_insufficient_stock(warehouse):
    with pytest.raises(ValueError, match="Недостатньо"):
        WriteOffOperation(3, "SKU-1", 10).execute(warehouse)

def test_operation_missing_item(warehouse):
    with pytest.raises(KeyError): ReceiptOperation(4, "UNKNOWN", 1).execute(warehouse)

def test_service_operation(service):
    result = service.apply_operation({"operation": "receipt", "operation_id": 10, "code": "SKU-1", "quantity": 2})
    assert result.quantity_after == 5

def test_service_bad_operation(service):
    with pytest.raises(ValueError): service.apply_operation({"operation": "invalid", "operation_id": 10, "code": "SKU-1", "quantity": 2})

def test_service_mock_return_value(warehouse, item):
    policy = Mock()
    policy.should_reorder.return_value = True
    policy.recommended_quantity.return_value = 17
    report = Mock()
    report.render.return_value = "MOCK REPORT"
    service = WarehouseService(warehouse, policy, report)
    assert service.reorder_suggestions() == ["SKU-1: замовити 17 од."]
    policy.should_reorder.assert_called_once_with(item)
    assert service.inventory_report() == "MOCK REPORT"
    report.render.assert_called_once()

def test_service_mock_side_effect(warehouse):
    policy = Mock()
    policy.should_reorder.side_effect = RuntimeError("Supplier offline")
    service = WarehouseService(warehouse, policy, Mock())
    with pytest.raises(RuntimeError, match="Supplier offline"): service.low_stock()
    policy.should_reorder.assert_called_once()

def test_service_no_reorder(warehouse):
    policy = Mock()
    policy.should_reorder.return_value = False
    service = WarehouseService(warehouse, policy, Mock())
    assert service.reorder_suggestions() == []
    policy.recommended_quantity.assert_not_called()
