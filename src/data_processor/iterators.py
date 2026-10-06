from collections.abc import Iterator


class InventoryCodeIterator:
    """One-shot iterator over warehouse codes."""

    def __init__(self, codes: list[str]) -> None:
        self._codes = codes
        self._index = 0

    def __iter__(self) -> "InventoryCodeIterator":
        return self

    def __next__(self) -> str:
        if self._index >= len(self._codes):
            raise StopIteration
        code = self._codes[self._index]
        self._index += 1
        return code


def inventory_code_iterator(codes: list[str]) -> Iterator[str]:
    for code in codes:
        yield code
