def recursive_factorial(n: int) -> int:
    if n == 0:
        return 1
    return n * recursive_factorial(n -1)


def iterative_factorial(n: int) -> int:
    result = 1
    if n == 0:
        return result
    for idx in range(1, n + 1):
        result *= idx
    return result
