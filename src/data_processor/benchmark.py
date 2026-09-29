from timeit import repeat
from .processors import create_inventory_index, find_product_by_code

def run_benchmark() -> list[tuple[int, float, float]]:
    results = []
    for size in (1_000, 10_000, 100_000):
        items = [{"code": f"P{i:06}", "name": f"Товар {i}", "category": "Тест", "quantity": i % 50, "price": float(i)} for i in range(size)]
        target = items[-1]["code"]  # найгірший випадок для лінійного пошуку
        index = create_inventory_index(items)
        list_time = min(repeat(lambda: find_product_by_code(items, target), number=100, repeat=5)) / 100
        dict_time = min(repeat(lambda: index.get(target), number=100, repeat=5)) / 100
        results.append((size, list_time, dict_time))
    return results

if __name__ == "__main__":
    for size, list_time, dict_time in run_benchmark():
        print(f"{size:>7} | {list_time:.8f} | {dict_time:.8f}")
