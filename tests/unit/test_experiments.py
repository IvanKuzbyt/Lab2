"""Reproducible experiments from the Lab 6 handout."""
from unittest.mock import Mock
import pytest
from warehouse_manager.models import Warehouse


def intentionally_buggy_total(price: float, quantity: int) -> float:
    """Deliberately incorrect example, not used by production code."""
    return price + quantity


def classify_stock(quantity: int) -> str:
    if quantity == 0:
        return "empty"
    if quantity <= 5:
        return "low"
    return "normal"


def test_weak_test_executes_without_verifying_result():
    intentionally_buggy_total(10, 2)  # passes, but incorrectly returns 12 instead of 20


def test_strong_test_detects_the_bug():
    with pytest.raises(AssertionError):
        assert intentionally_buggy_total(10, 2) == pytest.approx(20)


@pytest.mark.parametrize("quantity,expected", [(0, "empty"), (3, "low"), (10, "normal")])
def test_all_branches(quantity, expected):
    assert classify_stock(quantity) == expected


def test_mock_vs_fake_repository(item):
    fake = Warehouse(1, "Fake in-memory warehouse")
    fake.add_item(item)
    assert fake.find_by_code("SKU-1") is item
    mock = Mock()
    mock.find_by_code.return_value = item
    assert mock.find_by_code("SKU-1") is item
    mock.find_by_code.assert_called_once_with("SKU-1")
