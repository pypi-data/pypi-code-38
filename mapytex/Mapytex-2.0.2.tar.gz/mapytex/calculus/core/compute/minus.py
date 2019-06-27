#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 lafrite <lafrite@Poivre>
#
# Distributed under terms of the MIT license.

"""
Minus MO: take the opposit
"""

from multipledispatch import Dispatcher
from .exceptions import MinusError
from ..MO import MO, MOnumber, MOstr
from ..MO.fraction import MOFraction
from ..MO.monomial import MOstrPower, MOMonomial
from ..MO.polynomial import MOpolynomial
from ..tree import Tree

minus_doc = """ Opposite of a MO

:param left: None
:param right: right MO
:returns: Tree or MO

"""

minus = Dispatcher("minus", doc=minus_doc)


@minus.register(type(None), MOnumber)
def monumber(_, right):
    """

    >>> a = MOnumber(4)
    >>> minus(None, a)
    <MOnumber - 4>

    """
    return MO.factory(-right.value)


@minus.register(type(None), MOFraction)
def mofraction(_, right):
    """ 4 differents cases

    Either fraction , numerator or denominator is negative

    >>> a = MOFraction(6, 5)
    >>> print(minus(None, a))
    - 6 / 5

    The fraction is negative

    >>> a = MOFraction(6, 5, True)
    >>> print(minus(None, a))
    6 / 5

    Numerator is negative

    >>> a = MOFraction(-6, 5)
    >>> print(minus(None, a))
    6 / 5

    Denominators is negative

    >>> a = MOFraction(6, -5)
    >>> print(minus(None, a))
    6 / 5
    """
    if right.negative:
        return MOFraction(right._numerator, right._denominator)

    try:
        if right._numerator.value < 0:
            return MOFraction(-right._numerator.value, right._denominator)
    except TypeError:
        pass
    try:

        if right._denominator.value < 0:
            return MOFraction(right._numerator, -right._denominator.value)
    except TypeError:
        pass

    return MOFraction(right._numerator, right._denominator, True)


@minus.register(type(None), MOstr)
def mostr(_, right):
    """ Opposite of 'x' is '-x'

    :example:
    >>> x = MOstr("x")
    >>> print(minus(None, x))
    - x
    """
    return MOMonomial(-1, right)


@minus.register(type(None), MOstrPower)
def mostrpower(_, right):
    """ Opposite of 'x^n' is '-x^n'

    :example:
    >>> x2 = MOstrPower("x", 2)
    >>> print(minus(None, x2))
    - x^2
    """
    return MOMonomial(-1, right.variable, right.power)


@minus.register(type(None), MOMonomial)
def momonomial(_, right):
    """ Opposite of 'ax^n' is '-ax^n'

    :example:
    >>> tx2 = MOMonomial(3, "x", 2)
    >>> print(minus(None, tx2))
    - 3x^2
    """
    try:
        return MOMonomial(-right.coefficient.value, right.variable, right.power)
    except TypeError:
        coef = Tree("-", None, right.coefficient)
        return Tree("*", coef, right.strpower)


@minus.register(type(None), MOpolynomial)
def mopolynomial(_, right):
    """ Opposite of a polynomial

    :example:
    >>> P = MOpolynomial('x', [1, -2, 3])
    >>> print(minus(None, P))
    - 3x^2 + 2x - 1
    """
    neg_coefs = {p: -c.value for (p, c) in right.coefficients.items()}
    return MOpolynomial(right.variable, neg_coefs)


# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
