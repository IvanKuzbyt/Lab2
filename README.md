# Система потокової обробки складських запасів

**Курс:** Професійний Python  
**Лабораторна робота №3:** Ітератори, генератори та потокова обробка даних  
**Варіант №10:** Потокова обробка складських запасів  
**Студент:** Кузбит Іван Іванович

## Опис

Лабораторна робота є продовженням `warehouse_lab2`. Реалізовано потоковий конвеєр для обробки великого CSV-набору складських запасів без повного завантаження проміжних даних у пам'ять.

Формат основного набору:

```text
code,name,quantity,price,category
```

Окремий `data/operations.csv` використовується для потокової демонстрації надходжень (`receipt`) і списань (`issue`).

## Реалізовано

- iterable/iterator protocol та власний `InventoryCodeIterator`;
- generator functions і `yield`;
- `yield from`;
- generator expression;
- `itertools.islice`, `chain`, `accumulate`, `pairwise`;
- streaming CSV reader;
- parsing та validation;
- filtering і transformation stages;
- пошук позиції за кодом через lazy processing;
- streaming обчислення загальної вартості;
- lazy filter низького запасу;
- визначення мінімальної та максимальної ціни;
- valid/invalid records;
- batch processing;
- обробка надходжень і списань;
- eager/lazy comparison часу та peak memory;
- dataset на 100 000 записів;
- pytest-тести.

## Структура

```text
warehouse_lab3/
├── pyproject.toml
├── requirements.txt
├── README.md
├── .gitignore
├── data/
│   ├── inventory.csv
│   ├── operations.csv
│   └── demo_inventory.csv
├── src/
│   └── data_processor/
│       ├── __init__.py
│       ├── data.py
│       ├── processors.py
│       ├── analytics.py
│       ├── decorators.py
│       ├── benchmark.py
│       ├── models.py
│       ├── iterators.py
│       ├── readers.py
│       ├── parsers.py
│       ├── filters.py
│       ├── transformations.py
│       ├── batches.py
│       ├── pipeline.py
│       ├── experiments.py
│       ├── itertools_demo.py
│       └── main.py
└── tests/
    └── test_streaming.py
```

## Встановлення

Python 3.10 або новіший. У Git Bash / PowerShell у корені проєкту:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Git Bash:

```bash
source .venv/Scripts/activate
pip install -r requirements.txt
```

## Запуск

```bash
python -m src.data_processor.main
```

## Тести

```bash
pytest -q
```

## Експеримент eager/lazy

Основна програма автоматично вимірює час виконання та peak memory через `tracemalloc`. Отримані значення залежать від комп'ютера, версії Python та поточного навантаження системи, тому для звіту використовуються результати фактичного запуску.

## Поточна лабораторна

ЛР3 розширює ЛР2 потоковою моделлю обробки даних. Наступні лабораторні можуть використовувати цей самий модуль як ядро для тестування, БД, REST API, оптимізації та production-оточення.
