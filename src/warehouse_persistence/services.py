from .models import ProductRecord, StockOperationRecord

class InsufficientStockError(ValueError): pass

def change_stock(session, product_id, operation_type, amount):
    try:
        if operation_type not in ('receipt', 'write_off') or amount <= 0:
            raise ValueError('Invalid operation')
        item = session.get(ProductRecord, product_id)
        if item is None: raise LookupError('Product not found')
        if operation_type == 'write_off' and amount > item.quantity:
            raise InsufficientStockError('Insufficient stock')
        item.quantity += amount if operation_type == 'receipt' else -amount
        operation = StockOperationRecord(product_id=product_id, operation_type=operation_type, quantity=amount, quantity_after=item.quantity)
        session.add(operation)
        session.commit()
        session.refresh(operation)
        return operation
    except Exception:
        session.rollback()
        raise
