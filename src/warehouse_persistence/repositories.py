from decimal import Decimal
from sqlalchemy import func, select
from .models import ProductRecord, StockOperationRecord


class ProductRepository:
    def __init__(self, session):
        self.session = session

    def add(self, code, name, quantity, unit_price, minimum_stock=5):
        if not code.strip() or not name.strip() or quantity < 0 or Decimal(str(unit_price)) < 0 or minimum_stock < 0:
            raise ValueError("Invalid product")
        item = ProductRecord(
            code=code.strip().upper(),
            name=name.strip(),
            quantity=quantity,
            unit_price=Decimal(str(unit_price)),
            minimum_stock=minimum_stock,
        )
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def get(self, product_id):
        return self.session.get(ProductRecord, product_id)

    def by_code(self, code):
        return self.session.scalar(select(ProductRecord).where(ProductRecord.code == code.strip().upper()))

    def by_name(self, name):
        return list(self.session.scalars(select(ProductRecord).where(ProductRecord.name.contains(name))))

    def all(self):
        return list(self.session.scalars(select(ProductRecord).order_by(ProductRecord.id)))

    def update(self, product_id, *, name=None, unit_price=None, minimum_stock=None):
        item = self.get(product_id)
        if item is None:
            return None
        if name is not None:
            if not name.strip():
                raise ValueError("Invalid name")
            item.name = name.strip()
        if unit_price is not None:
            if Decimal(str(unit_price)) < 0:
                raise ValueError("Invalid price")
            item.unit_price = Decimal(str(unit_price))
        if minimum_stock is not None:
            if minimum_stock < 0:
                raise ValueError("Invalid minimum stock")
            item.minimum_stock = minimum_stock
        self.session.commit()
        return item

    def delete(self, product_id):
        item = self.get(product_id)
        if item is None:
            return False
        self.session.delete(item)
        self.session.commit()
        return True

    def total_value(self):
        return Decimal(
            str(self.session.scalar(select(func.sum(ProductRecord.quantity * ProductRecord.unit_price))) or 0)
        )

    def low_stock(self):
        return list(
            self.session.scalars(select(ProductRecord).where(ProductRecord.quantity <= ProductRecord.minimum_stock))
        )


class StockOperationRepository:
    def __init__(self, session):
        self.session = session

    def history(self, product_id):
        return list(
            self.session.scalars(
                select(StockOperationRecord)
                .where(StockOperationRecord.product_id == product_id)
                .order_by(StockOperationRecord.id)
            )
        )

    def get(self, operation_id):
        return self.session.get(StockOperationRecord, operation_id)
