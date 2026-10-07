"""Generic in-memory repositories."""

from typing import Generic, Protocol, TypeVar


class HasId(Protocol):
    id: int


T = TypeVar("T", bound=HasId)


class InMemoryRepository(Generic[T]):
    """Reusable repository for any entity with an integer id."""

    def __init__(self) -> None:
        self._items: dict[int, T] = {}

    def add(self, item: T) -> None:
        if item.id in self._items:
            raise ValueError(f"Об'єкт з ID {item.id} уже існує")
        self._items[item.id] = item

    def get(self, item_id: int) -> T | None:
        return self._items.get(item_id)

    def all(self) -> list[T]:
        return list(self._items.values())

    def remove(self, item_id: int) -> bool:
        return self._items.pop(item_id, None) is not None

    def __len__(self) -> int:
        return len(self._items)
