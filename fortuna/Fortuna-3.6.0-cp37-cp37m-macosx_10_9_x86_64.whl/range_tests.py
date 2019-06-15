from Fortuna import *


def numeric_limits():
    print("\nNumeric Input Limits:")
    print("\nInternal 64 bit Integer Type <long long>")
    exp_min_int = -9223372036854775807
    exp_max_int = 9223372036854775807
    print(f"Min Integer: { min_int()}{'' if min_int() == exp_min_int else f', expected: {exp_min_int}'}")
    print(f"Max Integer:  {max_int()}{'' if max_int() == exp_max_int else f', expected: {exp_max_int}'}")
    print("\nInternal 64 bit Float Type <double>")
    exp_min_float = -1.7976931348623157e+308
    exp_max_float = 1.7976931348623157e+308
    exp_neg_eps = -5e-324
    exp_pos_eps = 5e-324
    print(f"Min Float:   { min_float()}{'' if min_float() == exp_min_float else f', expected: {exp_min_float}'}")
    print(f"Max Float:    {max_float()}{'' if max_float() == exp_max_float else f', expected: {exp_max_float}'}")
    print(f"Neg Epsilon: { min_below()}{'' if min_below() == exp_neg_eps else f', expected: {exp_neg_eps}'}")
    print(f"Pos Epsilon:  {min_above()}{'' if min_above() == exp_pos_eps else f', expected: {exp_pos_eps}'}")


def range_accuracy(func: staticmethod, *args, expected_range, verbose=False, **kwargs):
    results = {func(*args, **kwargs) for _ in range(100000)}
    for itm in results:
        assert itm in expected_range, f"Range Error, range exceeded ({itm})."
    for itm in expected_range:
        assert itm in results, f"Range Warning, range not satisfied ({itm})."
    if verbose:
        print(f"{func.__name__}{args + tuple(kwargs)}: Success")


def range_tests():
    print("\nOutput Range Tests: ", end="")
    range_accuracy(random_below, 0, expected_range=(0,))
    range_accuracy(random_index, 0, expected_range=(-1,))
    range_accuracy(random_range, 0, expected_range=(0,))

    range_accuracy(random_below, 6, expected_range=range(6))
    range_accuracy(random_index, 6, expected_range=range(6))
    range_accuracy(random_range, 6, expected_range=range(6))

    range_accuracy(random_below, -6, expected_range=range(-5, 1))
    range_accuracy(random_index, -6, expected_range=range(-6, 0))
    range_accuracy(random_range, -6, expected_range=range(-6, 0))

    range_accuracy(random_int, -3, 3, expected_range=range(-3, 4))
    range_accuracy(random_int, 3, -3, expected_range=range(-3, 4))
    range_accuracy(random_range, -3, 3, expected_range=range(-3, 3))
    range_accuracy(random_range, 3, -3, expected_range=range(-3, 3))

    range_accuracy(random_range, 0, 12, 2, expected_range=range(0, 12, 2))
    range_accuracy(random_range, 12, 0, 2, expected_range=range(0, 12, 2))

    range_accuracy(random_range, -6, 6, 2, expected_range=range(-6, 6, 2))
    range_accuracy(random_range, 6, -6, 2, expected_range=range(-6, 6, 2))

    range_accuracy(random_range, -6, 6, -2, expected_range=(-4, -2, 0, 2, 4, 6))
    range_accuracy(random_range, 6, -6, -2, expected_range=(-4, -2, 0, 2, 4, 6))

    range_accuracy(random_range, 1, 20, -2, expected_range=range(2, 21, 2))
    range_accuracy(random_range, 1, 20, 2, expected_range=range(1, 20, 2))

    range_accuracy(d, 6, expected_range=[1, 2, 3, 4, 5, 6])
    range_accuracy(d, -6, expected_range=[-1, -2, -3, -4, -5, -6])
    range_accuracy(dice, 2, 6, expected_range=(2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12))
    range_accuracy(dice, -2, -6, expected_range=(2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12))

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

    print("Success!")


if __name__ == "__main__":
    numeric_limits()
    range_tests()
