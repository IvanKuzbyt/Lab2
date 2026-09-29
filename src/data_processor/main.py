from .data import products, STOCK_POLICY
from .processors import (get_unique_categories, create_inventory_index, find_product_by_code,
    get_low_stock_items, group_by_category, count_products_by_category, filter_by_category, sort_by_price)
from .analytics import calculate_total_value, find_most_expensive, calculate_average, create_product, create_stock_filter
from .benchmark import run_benchmark

def print_products(title: str, items: list[dict]) -> None:
    print(f"\n{title}")
    print("-" * 92)
    print(f"{'Код':<7} {'Назва':<27} {'Категорія':<27} {'К-сть':>6} {'Ціна':>10} {'Вартість':>12}")
    for p in items:
        print(f"{p['code']:<7} {p['name']:<27} {p['category']:<27} {p['quantity']:>6} {p['price']:>10.2f} {p['quantity']*p['price']:>12.2f}")

def main() -> None:
    print_products("Складські запаси", products)
    categories = get_unique_categories(products)
    print("\nУнікальні категорії:", ", ".join(sorted(categories)))
    print(f"Загальна вартість складу: {calculate_total_value(products):,.2f} грн")
    print("Найдорожча позиція:", find_most_expensive(products))
    print_products(f"Критичний запас (кількість <= {STOCK_POLICY[1]})", get_low_stock_items(products, STOCK_POLICY[1]))
    print("\nПошук за кодом A003:", find_product_by_code(products, "A003"))
    index = create_inventory_index(products)
    print("Пошук через dict-index D001:", index.get("D001"))
    print("\nГрупування за категоріями:")
    for category, entries in group_by_category(products).items():
        print(f"  {category}: {len(entries)} позицій")
    print("\nCounter категорій:", count_products_by_category(products))
    print_products("Сортування за ціною (спадання)", sort_by_price(products))
    selected = filter_by_category(products, "Периферія")
    print_products("Фільтр: Периферія", selected)
    low_filter = create_stock_filter(3)
    print("Closure (кількість <= 3):", [p["code"] for p in products if low_filter(p)])
    print("Середнє значення цін через *args:", calculate_average(799, 2499, 3299, 1699))
    added = create_product(code="E001", name="Кабель HDMI", category="Аксесуари", quantity=14, price=399.0)
    print("Запис через **kwargs:", added)
    print("\nBenchmark: найкращий час із 5 повторів, 100 пошуків у кожному повторі")
    print(f"{'N':>8} | {'list, с':>12} | {'dict, с':>12}")
    for n, lt, dt in run_benchmark():
        print(f"{n:>8} | {lt:>12.8f} | {dt:>12.8f}")

if __name__ == "__main__":
    main()
