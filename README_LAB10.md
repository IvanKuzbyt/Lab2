# Лабораторна робота №10 — Production Python

**Варіант 10:** система обліку складських запасів. Продовження лабораторних робіт №1–9.

## Встановлення (PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
python -m uvicorn warehouse_persistence.api:app --reload
```
Swagger: http://localhost:8000/docs; health: http://localhost:8000/health.

## Configuration
`APP_NAME`, `APP_ENV`, `LOG_LEVEL`, `DATABASE_URL`. За замовчуванням SQLite: `sqlite:///./data/warehouse.db`. Реальні secrets не додавати до `.env.example` або Git.

## Build / wheel
```powershell
python -m build
python -m venv .wheel-test
.\.wheel-test\Scripts\python.exe -m pip install (Get-ChildItem dist\*.whl | Select-Object -First 1).FullName
.\.wheel-test\Scripts\python.exe -m warehouse_manager.main
```

## Docker
```powershell
docker build -t warehouse-manager:1.0 .
docker run --rm -p 8000:8000 -v warehouse_data:/app/data -e APP_ENV=production -e DATABASE_URL=sqlite:////app/data/warehouse.db warehouse-manager:1.0
```
`/health` і `/docs` доступні на порту 8000. Іменований volume зберігає SQLite після видалення контейнера.

## CI/CD та перевірки
```powershell
python -m ruff check .
python -m ruff format --check .
python -m mypy src
python -m pytest -v
python -m build
```
Workflow `.github/workflows/ci.yml` запускається при push і pull request; виконує lint, format, type check, tests, wheel/sdist та Docker build. Успіх workflow потрібно підтвердити на GitHub Actions.

## API
`GET /health`, `GET/POST /products`, `GET/PATCH/DELETE /products/{product_id}`, `POST /products/{product_id}/incoming`, `POST /products/{product_id}/write-off`, `GET /stock/operations`, `GET /stock/value`, `GET /products/low-stock`. Заборонено списання понад залишок.

## Сценарій захисту
1. Продемонструвати структуру `src/` і залежності `pyproject.toml`.
2. Показати `.env.example` та `/health`.
3. Створити товар у Swagger, виконати надходження, списання, показати історію та заборону надмірного списання.
4. Запустити pytest, lint, type check, package build.
5. Побудувати Docker image, запустити контейнер із volume, перевірити `/health`.
6. Показати GitHub Actions і wheel/sdist.
