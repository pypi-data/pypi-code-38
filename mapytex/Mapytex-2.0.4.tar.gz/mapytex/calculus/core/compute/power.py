#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 lafrite <lafrite@Poivre>
#
# Distributed under terms of the MIT license.

"""
Power with MO
"""

from multipledispatch import Dispatcher
from ..tree import Tree
from ..MO import MO, MOnumber, MOstr
from ..MO.fraction import MOFraction
from ..MO.monomial import MOstrPower, MOMonomial
from ..MO.polynomial import MOpolynomial
from .filters import special_case

power_doc = """ Power of MOs

:param left: left MO
:param right: right MO
:returns: Tree or MO

"""

power = Dispatcher("power", doc=power_doc)


def power_filter(left, right):
    """ Automatic power on MO

    :param left: MO
    :param right: MO
    :returns: MO if it is a special case, nothing other wise

    >>> a = MOnumber(5)
    >>> b = MOnumber(1)
    >>> power(a, b)
    <MOnumber 5>
    >>> a = MOnumber(5)
    >>> b = MOnumber(0)
    >>> power(a, b)
    <MOnumber 1>
    >>> a = MOFraction(1, 2)
    >>> b = MOnumber(1)
    >>> power(a, b)
    <MOFraction 1 / 2>
    >>> a = MOFraction(1, 2)
    >>> b = MOnumber(0)
    >>> power(a, b)
    <MOnumber 1>
    """
    try:
        if right == 0:
            return MOnumber(1)
        elif right == 1:
            return left
    except TypeError:
        pass


@power.register(MOnumber, MOnumber)
@special_case(power_filter)
def monumber_monumber(left, right):
    """ Simply power values

    >>> a = MOnumber(4)
    >>> b = MOnumber(6)
    >>> power(a, b)
    <MOnumber 4096>

    """
    return MO.factory(left.value ** right.value)


@power.register(MOFraction, MOnumber)
@special_case(power_filter)
def mofraction_monumber(left, right):
    """ Return division Tree with on the numertor MOnumber times numerator of MOFraction

    >>> a = MOFraction(3, 2)
    >>> b = MOnumber(2)
    >>> print(power(a, b))
    /
     > ^
     | > 3
     | > 2
     > ^
     | > 2
     | > 2
    """
    num = Tree("^", left.numerator, right)
    denom = Tree("^", left.denominator, right)
    return Tree("/", num, denom)


@power.register(MOstrPower, MOnumber)
@special_case(power_filter)
def mostrpower_monumber(left, right):
    """ Multiply powers

    >>> P = MOstrPower("x", 4)
    >>> a = MOnumber(2)
    >>> print(power(P, a))
    ^
     > x
     > *
     | > 4
     | > 2
    """
    power = Tree("*", left.power, right)
    return Tree("^", left.variable, power)


@power.register(MOMonomial, MOnumber)
@special_case(power_filter)
def mostrpower_monumber(left, right):
    """ Multiply powers and raise coef to the power

    >>> P = MOMonomial(3,"x", 4)
    >>> a = MOnumber(2)
    >>> print(power(P, a))
    *
     > ^
     | > 3
     | > 2
     > ^
     | > x
     | > *
     | | > 4
     | | > 2
    """
    coef = Tree("^", left.coefficient, right)
    power = Tree("*", left.power, right)
    strpower = Tree("^", left.variable, power)
    return Tree("*", coef, strpower)


@power.register(MOpolynomial, MOnumber)
@special_case(power_filter)
def mopolynomial_monumber(left, right):
    """ Expand power to products of polynomials

    >>> P = MOpolynomial('x', [1, -2, 3])
    >>> a = MOnumber(2)
    >>> print(power(P, a))
    *
     > 3x^2 - 2x + 1
     > 3x^2 - 2x + 1
    """
    return Tree.from_list("*", [left] * right.value)


# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
