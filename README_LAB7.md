# ЛР7 — SQLite persistence, варіант 10

Продовження ЛР1–6. Старі модулі не видалено. Новий пакет: `src/warehouse_persistence/`.

## Установлення (PowerShell)
`python -m pip install -e ".[dev]"`

## Створення БД та міграції
`python -m alembic upgrade head`
`python -m alembic current`
`python -m alembic downgrade 001`
`python -m alembic upgrade head`

## Демонстрація
`python -m warehouse_persistence.main --db warehouse.db`

## Тести
`python -m pytest -v`
`python -m pytest -v tests/integration/test_database_lab7.py`

## SQLite запити
`SELECT * FROM products;`
`SELECT * FROM stock_operations;`
`SELECT p.code, p.name, o.operation_type, o.quantity FROM products p JOIN stock_operations o ON o.product_id = p.id;`

**Важливо:** `warehouse.db` є локальним файлом і не входить до Git; для створення використовуйте Alembic. Для тестів створюється окрема тимчасова SQLite база через `tmp_path`.
