#!/usr/bin/env python
# encoding: utf-8


__all__ = ["gcd"]


def gcd(a, b):
    """Compute gcd(a,b)

    :param a: first number (need to support abs, comparison, * and %)
    :param b: second number (need to support abs, comparison, * and %)
    :returns: the gcd

    >>> gcd(3, 15)
    3
    >>> gcd(15, 3)
    3
    >>> gcd(-3, -15)
    -3
    >>> gcd(5, 12)
    1
    >>> gcd(4, 14)
    2

    """
    try:
        pos_a, _a = (a >= 0), abs(a)
        pos_b, _b = (b >= 0), abs(b)

        gcd_sgn = -1 + 2 * (pos_a or pos_b)
    except TypeError:
        _a = a
        _b = b
        gcd_sgn = 1

    if _a > _b:
        c = _a % _b
    else:
        c = _b % _a

    if c == 0:
        return gcd_sgn * min(_a, _b)
    elif _a == 1:
        return gcd_sgn * _b
    elif _b == 1:
        return gcd_sgn * _a
    else:
        return gcd_sgn * gcd(min(_a, _b), c)


def lcm(a, b):
    """Compute lcm(a,b)

    :param a: first number (need to support abs, comparison, *, % and //)
    :param b: second number (need to support abs, comparison, *, % and //)
    :returns: the lcm

    >>> lcm(3, 15)
    15
    >>> lcm(15, 3)
    15
    >>> lcm(-3, -15)
    -15
    >>> lcm(5, 12)
    60
    >>> lcm(4, 14)
    28

    """
    return (a * b) // gcd(a, b)


if __name__ == "__main__":
    print(gcd(3, 15))
    print(gcd(3, 15))
    print(gcd(-15, -3))
    print(gcd(-3, -12))


# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
