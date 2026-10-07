# Експеримент зі статичною перевіркою типів

Методичка вимагає навмисно внести три помилки, запустити type checker, зафіксувати діагностику та виправити код. Щоб робочий проєкт завжди залишався коректним, приклади винесено в цей документ.

```python
customer_id: int = "1"  # error: incompatible assignment

def total() -> int:
    return "100"  # error: return type mismatch

# Якщо repository має тип InMemoryRepository[Product], наступний виклик
# некоректний: до репозиторію товарів передається Customer.
repository.add(customer)
```

Очікувані категорії діагностики mypy: incompatible types in assignment, incompatible return value type, incompatible argument type. Точний текст і номери рядків залежать від версії mypy та місця розміщення прикладів.

Виправлення: `customer_id = 1`, `return 100`, а до `InMemoryRepository[Product]` передавати лише об'єкт `Product`. Після виправлення запускається `python -m mypy src`.
