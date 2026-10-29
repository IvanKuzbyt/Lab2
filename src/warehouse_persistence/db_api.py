import sqlite3


def find_product(database_path, code):
    with sqlite3.connect(str(database_path)) as connection:
        connection.row_factory = sqlite3.Row
        row = connection.execute(
            "SELECT code, name, quantity, unit_price FROM products WHERE code = ?", (code.upper(),)
        ).fetchone()
        return dict(row) if row else None
