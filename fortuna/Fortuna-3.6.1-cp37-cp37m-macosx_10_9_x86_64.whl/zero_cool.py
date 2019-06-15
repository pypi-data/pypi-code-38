from Fortuna import *


def zero_cool_test(n):
    distribution_timer(random_index, n)

    distribution_timer(front_linear, n)
    distribution_timer(middle_linear, n)
    distribution_timer(back_linear, n)
    distribution_timer(quantum_linear, n)

    distribution_timer(front_gauss, n)
    distribution_timer(middle_gauss, n)
    distribution_timer(back_gauss, n)
    distribution_timer(quantum_gauss, n)

    distribution_timer(front_poisson, n)
    distribution_timer(middle_poisson, n)
    distribution_timer(back_poisson, n)
    distribution_timer(quantum_poisson, n)

    distribution_timer(quantum_monty, n)


if __name__ == "__main__":
    zero_cool_test(10)
    zero_cool_test(-10)
