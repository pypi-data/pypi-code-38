def recursive_fibonacci(n: int) -> int:
    if n >= 2:
        return recursive_fibonacci(n - 1) + recursive_fibonacci(n - 2)
    else:
        return n


def iterative_fibonacci(n: int) -> int:
    x, y = 0, 1
    for _ in range(0, n):
        x, y = y, x + y
    return x
