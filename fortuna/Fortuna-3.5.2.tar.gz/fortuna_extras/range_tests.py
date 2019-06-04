from Fortuna import *


def range_accuracy(func: staticmethod, *args, expected_range, **kwargs):
    results = {func(*args, **kwargs) for _ in range(100000)}
    for itm in results:
        assert itm in expected_range, "Range Error, range exceeded"
    for itm in expected_range:
        assert itm in results, f"Range Error, range not satisfied ({itm}). This may not be an error for rare values."
    # print(f"{func.__name__}{args + tuple(kwargs)}: Success")


def range_tests():
    range_accuracy(random_below, 0, expected_range=(0,))
    range_accuracy(random_index, 0, expected_range=(-1,))
    range_accuracy(random_range, 0, expected_range=(0,))

    range_accuracy(random_below, 6, expected_range=(0, 1, 2, 3, 4, 5))
    range_accuracy(random_index, 6, expected_range=(0, 1, 2, 3, 4, 5))
    range_accuracy(random_range, 6, expected_range=(0, 1, 2, 3, 4, 5))

    range_accuracy(random_below, -6, expected_range=(-5, -4, -3, -2, -1, 0))
    range_accuracy(random_index, -6, expected_range=(-6, -5, -4, -3, -2, -1))
    range_accuracy(random_range, -6, expected_range=(-6, -5, -4, -3, -2, -1))

    range_accuracy(random_int, -3, 3, expected_range=(-3, -2, -1, 0, 1, 2, 3))
    range_accuracy(random_range, -3, 3, expected_range=(-3, -2, -1, 0, 1, 2))
    range_accuracy(random_int, 3, -3, expected_range=(-3, -2, -1, 0, 1, 2, 3))
    range_accuracy(random_range, 3, -3, expected_range=(-3, -2, -1, 0, 1, 2))

    range_accuracy(random_range, -6, 6, 2, expected_range=(-6, -4, -2, 0, 2, 4))
    range_accuracy(random_range, -6, 6, -2, expected_range=(-4, -2, 0, 2, 4, 6))
    range_accuracy(random_range, 6, -6, 2, expected_range=(-6, -4, -2, 0, 2, 4))
    range_accuracy(random_range, 6, -6, -2, expected_range=(-4, -2, 0, 2, 4, 6))

    range_accuracy(d, 6, expected_range=[1, 2, 3, 4, 5, 6])
    range_accuracy(d, -6, expected_range=[-1, -2, -3, -4, -5, -6])

    range_accuracy(dice, 2, 6, expected_range=(2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12))
    range_accuracy(dice, -2, -6, expected_range=(2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12))
    range_accuracy(dice, 2, -6, expected_range=(-2, -3, -4, -5, -6, -7, -8, -9, -10, -11, -12))
    range_accuracy(dice, -2, 6, expected_range=(-2, -3, -4, -5, -6, -7, -8, -9, -10, -11, -12))

    range_accuracy(plus_or_minus, 3, expected_range=(-3, -2, -1, 0, 1, 2, 3))
    range_accuracy(plus_or_minus_linear, 3, expected_range=(-3, -2, -1, 0, 1, 2, 3))
    range_accuracy(plus_or_minus_gauss, 3, expected_range=(-3, -2, -1, 0, 1, 2, 3))
    range_accuracy(plus_or_minus_gauss, 100, expected_range=range(-100, 101))

    range_accuracy(front_gauss, 6, expected_range=range(6))
    range_accuracy(middle_gauss, 6, expected_range=range(6))
    range_accuracy(back_gauss, 6, expected_range=range(6))
    range_accuracy(quantum_gauss, 6, expected_range=range(6))
    range_accuracy(front_poisson, 6, expected_range=range(6))
    range_accuracy(middle_poisson, 6, expected_range=range(6))
    range_accuracy(back_poisson, 6, expected_range=range(6))
    range_accuracy(quantum_poisson, 6, expected_range=range(6))
    range_accuracy(front_linear, 6, expected_range=range(6))
    range_accuracy(middle_linear, 6, expected_range=range(6))
    range_accuracy(back_linear, 6, expected_range=range(6))
    range_accuracy(quantum_linear, 6, expected_range=range(6))
    range_accuracy(quantum_monty, 6, expected_range=range(6))

    range_accuracy(front_gauss, -6, expected_range=range(-6, 0))
    range_accuracy(middle_gauss, -6, expected_range=range(-6, 0))
    range_accuracy(back_gauss, -6, expected_range=range(-6, 0))
    range_accuracy(quantum_gauss, -6, expected_range=range(-6, 0))
    range_accuracy(front_poisson, -6, expected_range=range(-6, 0))
    range_accuracy(middle_poisson, -6, expected_range=range(-6, 0))
    range_accuracy(back_poisson, -6, expected_range=range(-6, 0))
    range_accuracy(quantum_poisson, -6, expected_range=range(-6, 0))
    range_accuracy(front_linear, -6, expected_range=range(-6, 0))
    range_accuracy(middle_linear, -6, expected_range=range(-6, 0))
    range_accuracy(back_linear, -6, expected_range=range(-6, 0))
    range_accuracy(quantum_linear, -6, expected_range=range(-6, 0))
    range_accuracy(quantum_monty, -6, expected_range=range(-6, 0))

    range_accuracy(percent_true, 50, expected_range=(True, False))
    range_accuracy(percent_true, 0.1, expected_range=(True, False))

    print("\nRange Accuracy: Success")


if __name__ == "__main__":
    range_tests()
