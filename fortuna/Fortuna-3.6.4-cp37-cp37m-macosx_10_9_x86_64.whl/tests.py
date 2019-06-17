import time as _time
import math as _math
import random as _random

from Fortuna import *
from fortuna_extras.range_tests import range_tests


def quick_test():
    test_warm_up()
    print("\nFortuna Quick Test")
    print("\nRandom Sequence Values:\n")
    start_test = _time.time()
    some_list = [i for i in range(10)]
    print(f"some_list = {some_list}\n")
    print("Base Case")
    distribution_timer(_random.choice, some_list, label="Random.choice(some_list)")
    distribution_timer(random_value, some_list, label="random_value(some_list)")
    truffle_shuffle = TruffleShuffle(some_list)
    distribution_timer(truffle_shuffle)
    some_tuple = tuple(i for i in range(10))
    monty = QuantumMonty(some_tuple)
    distribution_timer(monty)

    print("\nWeighted Tables:\n")
    population = ("A", "B", "C", "D")
    cum_weights = (1, 3, 6, 10)
    rel_weights = (1, 2, 3, 4)
    cum_weighted_table = zip(cum_weights, population)
    rel_weighted_table = zip(rel_weights, population)
    print(f"population = {population}")
    print(f"cum_weights = {cum_weights}  # partial_sum of rel_weights:  λ.xy: x + y")
    print(f"rel_weights = {rel_weights}  # adjacent_difference of cum_weights:  λ.xy: x - y")
    print(f"cum_weighted_table = ((1, 'A'), (3, 'B'), (6, 'C'), (10, 'D'))  # or zip(cum_weights, population)")
    print(f"rel_weighted_table = ((1, 'A'), (2, 'B'), (3, 'C'), (4, 'D'))  # or zip(rel_weights, population)\n")
    print("Cumulative Base Case")
    distribution_timer(
        _random.choices, population, cum_weights=cum_weights,
        label="Random.choices(population, cum_weights=cum_weights)"
    )
    cum_weighted_choice = CumulativeWeightedChoice(cum_weighted_table)
    distribution_timer(cum_weighted_choice)
    print("Relative Base Case")
    distribution_timer(
        _random.choices, population, weights=rel_weights,
        label="Random.choices(population, weights=rel_weights)"
    )
    rel_weighted_choice = RelativeWeightedChoice(rel_weighted_table)
    distribution_timer(rel_weighted_choice)

    print("\nRandom Matrix Values:\n")
    some_matrix = {"A": (1, 2, 3, 4), "B": (10, 20, 30, 40), "C": (100, 200, 300, 400)}
    print(f"some_matrix = {some_matrix}\n")
    flex_cat = FlexCat(some_matrix, key_bias="flat_uniform", val_bias="flat_uniform")
    distribution_timer(flex_cat)

    print("\nRandom Integers:\n")
    print("Base Case")
    distribution_timer(_random.randrange, 10)
    distribution_timer(random_below, 10)
    distribution_timer(random_index, 10)
    distribution_timer(random_range, 10)
    distribution_timer(random_below, -10)
    distribution_timer(random_index, -10)
    distribution_timer(random_range, -10)
    print("Base Case")
    distribution_timer(_random.randrange, 1, 10)
    distribution_timer(random_range, 1, 10)
    distribution_timer(random_range, 10, 1)
    print("Base Case")
    distribution_timer(_random.randint, -5, 5)
    distribution_timer(random_int, -5, 5)
    print("Base Case")
    distribution_timer(_random.randrange, 1, 20, 2)
    distribution_timer(random_range, 1, 20, 2)
    distribution_timer(random_range, 1, 20, -2)
    distribution_timer(d, 10)
    distribution_timer(dice, 3, 6)
    distribution_timer(ability_dice, 4)
    distribution_timer(plus_or_minus, 5)
    distribution_timer(plus_or_minus_linear, 5)
    distribution_timer(plus_or_minus_gauss, 5)

    print("\nRandom Floats:\n")
    print("Base Case")
    distribution_timer(_random.random, post_processor=round)
    distribution_timer(canonical, post_processor=round)
    distribution_timer(random_float, 0.0, 10.0, post_processor=_math.floor)

    print("\nRandom Booleans:\n")
    distribution_timer(percent_true, 33.33)

    print("\nShuffle Performance Tests:\n")
    med_size = 1000
    some_med_list = [i for i in range(med_size)]
    print(f"some_med_list = [i for i in range({med_size})]")
    print(f"\nBase Case: Random.shuffle(some_med_list)")
    shuffle_cycles = 8
    timer(_random.shuffle, some_med_list, cycles=shuffle_cycles)
    some_med_list.sort()
    print(f"\nfisher_yates(some_med_list)")
    timer(fisher_yates, some_med_list, cycles=shuffle_cycles)
    some_med_list.sort()
    print(f"\nknuth(some_med_list)")
    timer(knuth, some_med_list, cycles=shuffle_cycles)
    some_med_list.sort()
    print(f"\nshuffle(some_med_list)  # default shuffle is the knuth_b algorithm")
    timer(shuffle, some_med_list, cycles=shuffle_cycles)
    print()

    print("-" * 73)
    stop_test = _time.time()
    print(f"Total Test Time: {round(stop_test - start_test, 3)} seconds")


if __name__ == "__main__":

    print("\nFortuna Test Suite: RNG Storm Engine")
    range_tests()
    print(f"\n{'=' * 73}")
    quick_test()
    print(f"\n{'=' * 73}")
