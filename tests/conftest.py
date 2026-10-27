from decimal import Decimal
from pathlib import Path
import pytest
from warehouse_manager.models import Supplier, Product, WarehouseItem, Warehouse
from warehouse_manager.value_objects import Money
from warehouse_manager.services import WarehouseService, ThresholdReorderPolicy, ConsoleReportService

@pytest.fixture
def item():
    supplier = Supplier(1, "Test Supplier", "supplier@example.com")
    product = Product(1, "SKU-1", "Keyboard", "Electronics", Money(Decimal("12.50")), supplier)
    return WarehouseItem(1, product, 3, 5)

@pytest.fixture
def warehouse(item):
    stock = Warehouse(1, "Test warehouse")
    stock.add_item(item)
    return stock

@pytest.fixture
def service(warehouse):
    return WarehouseService(warehouse, ThresholdReorderPolicy(5, 20), ConsoleReportService())

@pytest.fixture
def csv_file(tmp_path):
    file = tmp_path / "inventory.csv"
    file.write_text("code,name,quantity,price,category\nSKU-1,Keyboard,3,12.50,Electronics\nSKU-2,Mouse,0,5.00,Electronics\n", encoding="utf-8")
    return file
