"""Immutable value objects used by the warehouse domain."""

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation


@dataclass(frozen=True, slots=True)
class Money:
    """Money amount in a single currency, immutable after construction."""

    amount: Decimal
    currency: str = "UAH"

    def __post_init__(self) -> None:
        try:
            normalized = Decimal(str(self.amount)).quantize(Decimal("0.01"))
        except (InvalidOperation, ValueError) as error:
            raise ValueError("Некоректна грошова сума") from error
        if normalized < 0:
            raise ValueError("Грошова сума не може бути від'ємною")
        if not self.currency or len(self.currency) != 3:
            raise ValueError("Код валюти має містити три символи")
        object.__setattr__(self, "amount", normalized)
        object.__setattr__(self, "currency", self.currency.upper())

    def __add__(self, other: object) -> "Money":
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise ValueError("Не можна додавати різні валюти")
        return Money(self.amount + other.amount, self.currency)

    def __mul__(self, quantity: int) -> "Money":
        if quantity < 0:
            raise ValueError("Кількість не може бути від'ємною")
        return Money(self.amount * quantity, self.currency)

    def __str__(self) -> str:
        return f"{self.amount:.2f} {self.currency}"
