from itertools import accumulate, chain, count, islice, pairwise


def demonstrate_itertools() -> dict[str, list]:
    infinite = count(1)
    first_five = list(islice(infinite, 5))
    chained = list(chain(["A001", "A002"], ["B001"]))
    cumulative = list(accumulate([10, 20, 30]))
    differences = [current - previous for previous, current in pairwise([100, 104, 101, 110])]
    return {
        "islice": first_five,
        "chain": chained,
        "accumulate": cumulative,
        "pairwise": differences,
    }
