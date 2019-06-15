from Fortuna import *


def flex_cat_tests():
    print("\nFlexCat Test Suite\n")

    some_matrix = {
        "A": (1, 2, 3),
        "B": (10, 20, 30),
        "C": (100, 200, 300),
    }

    str_zero_cool_dispatch = (
        "front_linear", "middle_linear", "back_linear", "quantum_linear",
        "front_gauss", "middle_gauss", "back_gauss", "quantum_gauss",
        "front_poisson", "middle_poisson", "back_poisson", "quantum_poisson",
        "quantum_monty", "flat_uniform",
    )

    for v_bias in str_zero_cool_dispatch:
        for k_bias in str_zero_cool_dispatch:
            f_cat = FlexCat(some_matrix, key_bias=k_bias, val_bias=v_bias)
            distribution_timer(f_cat, num_cycles=1000)


if __name__ == "__main__":
    flex_cat_tests()
