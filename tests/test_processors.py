import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
from data_processor.data import products
from data_processor.processors import get_unique_categories, create_inventory_index, find_product_by_code, get_low_stock_items, group_by_category, count_products_by_category
from data_processor.analytics import calculate_total_value, find_most_expensive, create_stock_filter

def test_index_and_search():
    index = create_inventory_index(products)
    assert index["A001"]["name"] == "Ноутбук Lenovo"
    assert find_product_by_code(products, "a003")["code"] == "A003"

def test_aggregations_and_groups():
    assert round(calculate_total_value(products), 2) == 468479.00
    assert len(get_unique_categories(products)) == 6
    assert sum(count_products_by_category(products).values()) == len(products)
    assert len(group_by_category(products)["Периферія"]) == 3

def test_filters_and_max():
    assert {p["code"] for p in get_low_stock_items(products)} == {"A001", "A003", "B003", "C002", "D001"}
    assert find_most_expensive(products)["code"] == "D001"
    assert [p["code"] for p in products if create_stock_filter(3)(p)] == ["A003", "B003", "D001"]
