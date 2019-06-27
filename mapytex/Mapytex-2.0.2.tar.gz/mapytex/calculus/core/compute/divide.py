#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 lafrite <lafrite@Poivre>
#
# Distributed under terms of the MIT license.

"""
Divide MO
"""

from decimal import Decimal
from multipledispatch import Dispatcher
from ..tree import Tree
from ..MO import MO, MOnumber
from ..MO.fraction import MOFraction
from .exceptions import DivideError
from .filters import special_case

divide_doc = """ Dividing MOs

:param left: left MO
:param right: right MO
:returns: Tree or MO

"""

divide = Dispatcher("divide", doc=divide_doc)


def divide_filter(left, right):
    """ Automatic divide on MO

    >>> a = MOnumber(4)
    >>> b = MOnumber(1)
    >>> divide(a, b)
    <MOnumber 4>
    >>> a = MOnumber(0)
    >>> b = MOnumber(1)
    >>> divide(a, b)
    <MOnumber 0>
    >>> a = MOnumber(4)
    >>> b = MOnumber(0)
    >>> divide(a, b)
    Traceback (most recent call last):
        ...
    mapytex.calculus.core.compute.exceptions.DivideError: Division by zero
    """
    try:
        if left == 0:
            return left
    except TypeError:
        pass
    try:
        if right == 1:
            return left
    except TypeError:
        pass
    try:
        if right == 0:
            raise DivideError("Division by zero")
    except TypeError:
        pass


@divide.register(MOnumber, MOnumber)
@special_case(divide_filter)
def monumber_monumber(left, right):
    """ Divide 2 monumbers and return a MOFraction

    >>> a = MOnumber(4)
    >>> b = MOnumber(6.2)
    >>> monumber_monumber(a, b)
    <MOnumber 0.6451612903225806266768278939>
    >>> a = MOnumber(4)
    >>> b = MOnumber(6)
    >>> monumber_monumber(a, b)
    Traceback (most recent call last):
    ...
    NotImplementedError: Can't divide 2 int. Need to create a Fraction instead
    """
    if type(left.value) in [float, Decimal] or type(right.value) in [float, Decimal]:
        return MO.factory(left.value / right.value)
    else:
        raise NotImplementedError(
            "Can't divide 2 int. Need to create a Fraction instead"
        )


@divide.register(MOnumber, MOFraction)
@special_case(divide_filter)
def monumber_mofraction(left, right):
    """ Divide a monumber and a mofraction by inverting MOFraction

    >>> a = MOnumber(4)
    >>> b = MOFraction(6, 5)
    >>> print(divide(a, b))
    *
     > 4
     > 5 / 6
    >>> b = MOFraction(6, 5, True)
    >>> print(divide(a, b))
    *
     > 4
     > - 5 / 6
    """
    return Tree("*", left, right.inverse())


@divide.register(MOFraction, MOnumber)
@special_case(divide_filter)
def mofraction_monumber(left, right):
    """ Divide a monumber and a mofraction by inverting MOnumber

    >>> a = MOFraction(6, 5)
    >>> b = MOnumber(4)
    >>> print(mofraction_monumber(a, b))
    *
     > 6 / 5
     > 1 / 4
    """

    right_fraction = MOFraction(MOnumber(1), right)
    return Tree("*", left, right_fraction)


@divide.register(MOFraction, MOFraction)
@special_case(divide_filter)
def mofraction_mofraction(left, right):
    """ Divide two mofractions by inverting right MOFraction

    >>> a = MOFraction(1, 5)
    >>> b = MOFraction(4, 5)
    >>> print(mofraction_mofraction(a, b))
    *
     > 1 / 5
     > 5 / 4

    """
    return Tree("*", left, right.inverse())


# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
