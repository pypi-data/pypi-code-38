from Fortuna import quick_test
from fortuna_extras.range_tests import range_tests


if __name__ == "__main__":

    print("\nFortuna Test Suite: RNG Storm Engine")
    range_tests()
    print(f"\n{'=' * 73}")
    quick_test()
