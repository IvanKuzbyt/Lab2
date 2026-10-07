"""Warehouse domain entities."""

from dataclasses import dataclass, field
from decimal import Decimal
from collections.abc import Iterator

from warehouse_manager.value_objects import Money


@dataclass(slots=True)
class Supplier:
    id: int
    name: str
    email: str

    def __post_init__(self) -> None:
        if self.id <= 0 or not self.name.strip() or "@" not in self.email:
            raise ValueError("Некоректні дані постачальника")


@dataclass(slots=True)
class Product:
    id: int
    code: str
    name: str
    category: str
    _price: Money
    supplier: Supplier

    def __post_init__(self) -> None:
        if self.id <= 0 or not self.code.strip() or not self.name.strip():
            raise ValueError("ID, код і назва товару мають бути заповнені")

    @property
    def price(self) -> Money:
        """Return the current validated unit price."""
        return self._price

    @price.setter
    def price(self, value: Money) -> None:
        if not isinstance(value, Money):
            raise TypeError("Ціна має бути об'єктом Money")
        self._price = value

    def __str__(self) -> str:
        return f"{self.code} — {self.name} ({self.price})"


@dataclass(slots=True)
class WarehouseItem:
    id: int
    product: Product
    _quantity: int
    low_stock_threshold: int = 5

    def __post_init__(self) -> None:
        if self.id <= 0 or self._quantity < 0 or self.low_stock_threshold < 0:
            raise ValueError("Некоректна кількість або поріг залишку")

    @property
    def quantity(self) -> int:
        return self._quantity

    @property
    def total_value(self) -> Money:
        return self.product.price * self.quantity

    @property
    def is_low_stock(self) -> bool:
        return self.quantity <= self.low_stock_threshold

    def receive(self, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("Кількість надходження має бути додатною")
        self._quantity += quantity

    def write_off(self, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("Кількість списання має бути додатною")
        if quantity > self._quantity:
            raise ValueError("Недостатньо товару для списання")
        self._quantity -= quantity

    def __repr__(self) -> str:
        return (f"WarehouseItem(id={self.id}, code={self.product.code!r}, "
                f"quantity={self.quantity})")


@dataclass(slots=True)
class Warehouse:
    id: int
    name: str
    _items: dict[str, WarehouseItem] = field(default_factory=dict)

    def add_item(self, item: WarehouseItem) -> None:
        code = item.product.code.upper()
        if code in self._items:
            raise ValueError(f"Товар {code} уже є на складі")
        self._items[code] = item

    def find_by_code(self, code: str) -> WarehouseItem | None:
        return self._items.get(code.upper())

    @property
    def items(self) -> tuple[WarehouseItem, ...]:
        return tuple(self._items.values())

    @property
    def total_value(self) -> Money:
        total = Money(Decimal("0.00"))
        for item in self._items.values():
            total = total + item.total_value
        return total

    def low_stock_items(self) -> list[WarehouseItem]:
        return [item for item in self._items.values() if item.is_low_stock]

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[WarehouseItem]:
        return iter(self._items.values())

    def __contains__(self, code: object) -> bool:
        return isinstance(code, str) and code.upper() in self._items


@dataclass(frozen=True, slots=True)
class StockOperationResult:
    operation_id: int
    code: str
    operation: str
    quantity: int
    quantity_after: int

    def __str__(self) -> str:
        return (f"Операція #{self.operation_id}: {self.operation} {self.code}, "
                f"кількість після операції: {self.quantity_after}")
