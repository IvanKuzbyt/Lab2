# Система обліку складських запасів — лабораторна робота №4

**Курс:** Професійний Python  
**Варіант:** 10 — система обліку складських запасів  
**Студент:** Кузбит Іван Іванович

## Продовження лабораторної роботи №3

Проєкт створено на основі наданого архіву `warehouse_lab3`, а не як окрему незалежну програму. Збережено каталог `data/` з `inventory.csv` (100 000 рядків даних), `operations.csv`, `demo_inventory.csv`, пакет `data_processor` з reader/parser/validation/transformations/pipeline, аналітикою, batching, itertools та eager/lazy експериментами, а також попередні потокові тести.

У лабораторній №4 додано пакет `warehouse_manager`, який перетворює записи `InventoryRecord` із потокового конвеєра на доменні об'єкти `Product`, `WarehouseItem` і `Warehouse`. Повний CSV обробляється потоково для статистики; об'єктна модель для демонстрації створюється на обмеженій вибірці з перших 10 валідних записів. Операції для демонстрації беруться з наявного `data/operations.csv`.

## ООП і система типів

- dataclass-моделі та immutable value object `Money`;
- інкапсуляція, properties і перевірка складських залишків;
- наслідування та поліморфізм для надходження/списання через `ABC`;
- композиція складу, позицій, товарів і постачальника;
- `Protocol`, dependency injection і розділені сервіси;
- generic repository `InMemoryRepository[T]`, `TypeVar` з bound `HasId`, `TypedDict`;
- dunder methods, принципи SOLID і конфігурація mypy strict.

## Встановлення у Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

## Запуск

```powershell
python -m warehouse_manager.main
```

Попередня потокова демонстрація ЛР3 також збережена:

```powershell
python -m data_processor.main
```

## Тести та перевірка типів

```powershell
python -m pytest -q
python -m mypy src
```

Type-checking experiment наведено в `docs/type_checking_experiment.md`. Навмисні помилки потрібно перевірити в окремому тимчасовому файлі, зафіксувати фактичні diagnostics, а потім видалити його. У середовищі створення архіву встановити mypy через мережу не вдалося, тому успішний запуск mypy не заявляється.
