# Лабораторна робота №6 — автоматизоване тестування

Варіант 10: система обліку складських запасів. Проєкт продовжує ЛР1–5 без видалення попередніх модулів.

## Встановлення (Python 3.11+)

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

## Команди

```powershell
python -m pytest -q
python -m pytest -v --cov=reliable_importer --cov=warehouse_manager --cov-branch --cov-report=term-missing --cov-report=html
python -m pytest -m integration -v
python -m pytest -m "not integration" -v
python -m reliable_importer.main --config config.yaml
```

HTML-звіт: `htmlcov/index.html`. Усі нові тести містяться в `tests/unit/` та `tests/integration/`; тести ЛР1–5 збережені.

У `tests/unit/test_async.py` AsyncMock ілюструє контракт майбутнього асинхронного постачальника: основний застосунок наразі не має мережевих async-залежностей.

## Покриття всіх історичних пакетів

Для всього накопиченого репозиторію разом із data_processor результат становить 70%; для двох пакетів, на які орієнтована ЛР6, — 82%. Повне покриття попередніх лабораторних потребує додаткових тестів.
