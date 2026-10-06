from collections import Counter
from itertools import islice
from pathlib import Path

from .analytics import apply_operations, count_categories, count_valid_invalid, find_min_max_price, streaming_average_price, calculate_total_value
from .batches import batched
from .experiments import run_eager_lazy_experiment
from .iterators import InventoryCodeIterator
from .itertools_demo import demonstrate_itertools
from .pipeline import build_pipeline, build_low_stock_pipeline
from .readers import read_csv_rows

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"


def main() -> None:
    inventory_path = DATA / "inventory.csv"
    operations_path = DATA / "operations.csv"

    print("=== Лабораторна робота №3: потокова обробка складських запасів ===")
    print("Варіант №10 | Кузбит Іван Іванович")

    first_records = list(islice(build_pipeline(inventory_path), 5))
    print("\nПерші 5 валідних записів:")
    for record in first_records:
        print(record)

    print("\nПошук позиції за кодом INV000010:")
    found = next((r for r in build_pipeline(inventory_path) if r.code == "INV000010"), None)
    print(found)

    low_stock = list(islice(build_low_stock_pipeline(inventory_path, 5), 5))
    print("\nПерші 5 позицій з низьким запасом (<= 5):")
    for record in low_stock:
        print(record.code, record.name, record.quantity)

    total = calculate_total_value(build_pipeline(inventory_path))
    minimum, maximum = find_min_max_price(build_pipeline(inventory_path))
    average = streaming_average_price(build_pipeline(inventory_path))
    valid, invalid = count_valid_invalid(read_csv_rows(inventory_path))
    categories = count_categories(build_pipeline(inventory_path))

    print(f"\nВалідних записів: {valid}")
    print(f"Невалідних записів: {invalid}")
    print(f"Загальна вартість складу: {total:,.2f} грн")
    print(f"Мінімальна ціна: {minimum:.2f} грн")
    print(f"Максимальна ціна: {maximum:.2f} грн")
    print(f"Середня ціна: {average:.2f} грн")
    print("Топ категорій:", categories.most_common(5))

    print("\nBatch processing (перші 2 batches по 5 записів):")
    for index, batch in enumerate(batched(build_pipeline(inventory_path), 5)):
        print(f"Batch {index + 1}: {len(batch)} records")
        if index == 1:
            break

    base_records = list(islice(build_pipeline(inventory_path), 100))
    codes = [record.code for record in base_records]
    print("\nВласний iterator:", list(InventoryCodeIterator(codes[:5])))

    print("\nІнструменти itertools:", demonstrate_itertools())

    stock = apply_operations(
        (record for record in base_records),
        read_csv_rows(operations_path),
    )
    print(f"Поточна кількість INV000001 після надходжень/списань: {stock.get('INV000001')}")

    print("\nEager vs Lazy experiment:")
    experiment = run_eager_lazy_experiment(inventory_path)
    for mode, (elapsed, memory) in experiment.items():
        print(f"{mode.capitalize():<6}: time={elapsed:.6f} s, peak_memory={memory:.3f} MB")


if __name__ == "__main__":
    main()
