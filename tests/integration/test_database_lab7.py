"""Lab 7 isolated integration tests; each test uses its own SQLite database."""
from decimal import Decimal
import sqlite3
import pytest
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError
from warehouse_persistence.database import make_engine, make_session_factory
from warehouse_persistence.models import Base, ProductRecord, StockOperationRecord
from warehouse_persistence.repositories import ProductRepository, StockOperationRepository
from warehouse_persistence.services import change_stock, InsufficientStockError
from warehouse_persistence.db_api import find_product

@pytest.fixture
def db(tmp_path):
    path = tmp_path / 'test.db'
    engine = make_engine(path)
    Base.metadata.create_all(engine)
    with make_session_factory(engine)() as session:
        yield path, session
    engine.dispose()

@pytest.fixture
def product(db):
    _, session = db
    return ProductRepository(session).add('A-001', 'Гайка', 10, Decimal('2.50'), 5)

def test_create_read(db, product):
    _, s = db
    assert ProductRepository(s).get(product.id).code == 'A-001'

def test_update(db, product):
    _, s = db
    item = ProductRepository(s).update(product.id, name='Гвинт', unit_price=Decimal('3.00'))
    assert item.name == 'Гвинт' and item.unit_price == Decimal('3.00')

def test_delete(db, product):
    _, s = db
    repo = ProductRepository(s)
    assert repo.delete(product.id) is True
    assert repo.get(product.id) is None
    assert repo.delete(product.id) is False

def test_search_by_code_and_name(db, product):
    _, s = db
    repo = ProductRepository(s)
    assert repo.by_code('a-001').id == product.id
    assert repo.by_name('Гай')[0].id == product.id

def test_total_value(db, product):
    _, s = db
    assert ProductRepository(s).total_value() == Decimal('25.00')

def test_low_stock(db, product):
    _, s = db
    change_stock(s, product.id, 'write_off', 5)
    assert ProductRepository(s).low_stock()[0].code == 'A-001'

def test_receipt_and_history(db, product):
    _, s = db
    result = change_stock(s, product.id, 'receipt', 3)
    assert result.quantity_after == 13
    assert StockOperationRepository(s).history(product.id)[0].operation_type == 'receipt'

def test_writeoff(db, product):
    _, s = db
    assert change_stock(s, product.id, 'write_off', 4).quantity_after == 6

def test_rollback_insufficient_stock(db, product):
    _, s = db
    with pytest.raises(InsufficientStockError):
        change_stock(s, product.id, 'write_off', 100)
    s.expire_all()
    assert ProductRepository(s).get(product.id).quantity == 10
    assert StockOperationRepository(s).history(product.id) == []

def test_invalid_operation_rollback(db, product):
    _, s = db
    with pytest.raises(ValueError): change_stock(s, product.id, 'unknown', 2)
    assert ProductRepository(s).get(product.id).quantity == 10

def test_missing_product(db):
    _, s = db
    with pytest.raises(LookupError): change_stock(s, 9999, 'receipt', 1)

def test_db_api_parameterized(db, product):
    path, _ = db
    assert find_product(path, 'A-001')['name'] == 'Гайка'
    assert find_product(path, "A-001' OR 1=1 --") is None

def test_unique_constraint(db, product):
    _, s = db
    with pytest.raises(IntegrityError):
        ProductRepository(s).add('A-001', 'Duplicate', 1, Decimal('1.00'))
    s.rollback()

def test_fk_constraint(db):
    _, s = db
    s.add(StockOperationRecord(product_id=999, operation_type='receipt', quantity=1, quantity_after=1))
    with pytest.raises(IntegrityError): s.commit()
    s.rollback()

def test_check_constraint(db):
    _, s = db
    s.add(ProductRecord(code='NEG', name='Bad', quantity=-1, unit_price=Decimal('1.00'), minimum_stock=5))
    with pytest.raises(IntegrityError): s.commit()
    s.rollback()

def test_delete_cascades_history(db, product):
    _, s = db
    change_stock(s, product.id, 'receipt', 1)
    ProductRepository(s).delete(product.id)
    assert StockOperationRepository(s).history(product.id) == []

def test_two_related_tables(db):
    _, s = db
    names = inspect(s.bind).get_table_names()
    assert 'products' in names and 'stock_operations' in names
