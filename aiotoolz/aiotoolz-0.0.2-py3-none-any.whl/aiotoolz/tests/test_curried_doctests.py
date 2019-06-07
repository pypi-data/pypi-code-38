import doctest
import aiotoolz


def test_doctests():
    aiotoolz.__test__ = {}
    for name, func in vars(aiotoolz).items():
        if isinstance(func, aiotoolz.curry):
            aiotoolz.__test__[name] = func.func
    assert doctest.testmod(aiotoolz).failed == 0
    del aiotoolz.__test__
