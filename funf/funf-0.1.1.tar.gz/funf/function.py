from .__func_fibbnacci import Fibb_series, Find_Fibb
from .__func_gcd import GCD


def fibonacci(x, y=None):
    if not y:
        return Find_Fibb(x)
    else:
        Fibb_series(x, y)


def gcd(x, y):
    return GCD(x, y)


def ash():
    print("Hello My Name is Ashvini jangid")
