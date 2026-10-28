# Лабораторна робота №8 — REST API та асинхронність (варіант 10)

Проєкт **продовжує ЛР1–7**, зберігає SQLite, ORM, Repository Pattern та транзакційний облік руху запасів.

## Windows PowerShell

```powershell
python -m pip install -e ".[dev]"
python -m alembic upgrade head
python -m uvicorn warehouse_persistence.api:app --reload
```

Відкрийте у браузері `http://127.0.0.1:8000/docs` (Swagger UI), `http://127.0.0.1:8000/redoc`.

## Основні endpoints

| Метод | Шлях | Призначення |
|---|---|---|
| GET | `/products` | Список, пошук `?name=`, `?code=`, `?limit=` |
| GET | `/products/{product_id}` | Перегляд товару |
| POST | `/products` | Додати товар |
| PATCH | `/products/{product_id}` | Редагувати товар |
| DELETE | `/products/{product_id}` | Видалити товар |
| GET | `/products/low-stock` | Товари з низьким запасом |
| POST | `/products/{product_id}/incoming` | Надходження |
| POST | `/products/{product_id}/write-off` | Списання із захистом від від’ємного залишку |
| GET | `/stock/operations` | Історія руху; `?product_id=` |
| GET | `/stock/value` | Вартість складу |
| POST | `/products/batch-check` | Асинхронна перевірка декількох товарів через HTTPX |

Для batch-check API має працювати на `127.0.0.1:8000` або потрібно передати правильний `base_url`.

## Тести

```powershell
python -m pytest -v
```

Тести API використовують окрему тимчасову SQLite-базу та ASGITransport; запуск реального сервера для тестів не потрібен.
