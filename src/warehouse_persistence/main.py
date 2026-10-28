import argparse
from decimal import Decimal
from sqlalchemy import inspect
from .database import make_engine, make_session_factory
from .models import Base
from .repositories import ProductRepository, StockOperationRepository
from .services import change_stock
from .db_api import find_product

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', default='warehouse.db')
    args = parser.parse_args()
    engine = make_engine(args.db)
    if not inspect(engine).has_table('products'): Base.metadata.create_all(engine)
    with make_session_factory(engine)() as session:
        repo = ProductRepository(session)
        item = repo.by_code('LAB7-001') or repo.add('LAB7-001', 'Демонстраційний товар', 10, Decimal('125.50'))
        change_stock(session, item.id, 'receipt', 4)
        change_stock(session, item.id, 'write_off', 2)
        print('Products:', [(p.code, p.quantity) for p in repo.all()])
        print('Warehouse value:', repo.total_value())
        print('Low stock:', [p.code for p in repo.low_stock()])
        print('History:', [(o.operation_type, o.quantity) for o in StockOperationRepository(session).history(item.id)])
        print('DB-API:', find_product(args.db, 'LAB7-001'))
if __name__ == '__main__': main()
