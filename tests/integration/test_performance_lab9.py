import pytest
from warehouse_persistence.analytics import (
    generate_catalog,
    statistics_python,
    statistics_numpy,
    WarehouseStatisticsCache,
    operation_statistics,
)
from warehouse_persistence.parallel import (
    total_value_threads,
    total_value_processes,
    thread_example,
    process_example,
    concurrent_stock_updates,
    race_condition_demo,
    load_journals_sequential,
    load_journals_threads,
)
from warehouse_persistence.profiling import profile_catalog, memory_profile


def test_numpy_matches_python():
    items = generate_catalog(1000)
    expected = statistics_python(items)
    actual = statistics_numpy(items)
    for key in expected:
        assert actual[key] == pytest.approx(expected[key], rel=1e-10, abs=1e-6)


def test_thread_pool():
    items = generate_catalog(1000)
    assert total_value_threads(items, 4) == pytest.approx(statistics_python(items)["total_value"])


def test_process_pool():
    items = generate_catalog(1000)
    assert total_value_processes(items, 2) == pytest.approx(statistics_python(items)["total_value"])


def test_thread_and_process():
    assert thread_example([2, 3, 4]) == [4, 9, 16]
    assert process_example(5) == 25


def test_race_and_lock():
    assert race_condition_demo(4, 10) == 10
    assert concurrent_stock_updates(0, 4, 100) == 400


def test_cache_invalidation():
    items = [(10, 10.0, 2)]
    cache = WarehouseStatisticsCache(lambda: items)
    assert cache.statistics()["total_value"] == 100
    assert cache.statistics()["total_value"] == 100
    assert cache.cache_info().hits >= 1
    items[0] = (15, 10.0, 2)
    cache.record_movement()
    assert cache.statistics()["total_value"] == 150


def test_movement_statistics():
    assert operation_statistics([("A", "receipt", 4), ("A", "write_off", 2)])["A"] == {"receipt": 4, "write_off": 2}


def test_profile():
    items = generate_catalog(100)
    result, output = profile_catalog(items)
    assert result["total_value"] > 0 and "statistics_python" in output
    result, current, peak = memory_profile(items)
    assert result["total_value"] > 0 and peak >= current >= 0


def test_journals(tmp_path):
    paths = []
    for i in range(3):
        path = tmp_path / f"journal_{i}.csv"
        path.write_text("code,operation,quantity\nA,receipt,4\n", encoding="utf-8")
        paths.append(path)
    assert load_journals_sequential(paths) == load_journals_threads(paths, 2)


def test_empty_catalog_rejected():
    with pytest.raises(ValueError):
        statistics_python([])
    with pytest.raises(ValueError):
        generate_catalog(0)
