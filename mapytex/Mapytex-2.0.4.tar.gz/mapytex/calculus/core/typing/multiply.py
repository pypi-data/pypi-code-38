#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 lafrite <lafrite@Poivre>
#
# Distributed under terms of the MIT license.

"""
Multiply MO with typing
"""

from multipledispatch import Dispatcher
from ..tree import Tree
from ..MO import MO, MOnumber, MOstr
from ..MO.fraction import MOFraction
from ..MO.monomial import MOstrPower, MOMonomial

multiply_doc = """ Multiply MOs

:param left: left MO
:param right: right MO
:returns: MO

"""

multiply = Dispatcher("multiply", doc=multiply_doc)


@multiply.register((MOnumber, MOFraction), MOstr)
def moscalar_mostr(left, right):
    """ Multiply a scalar with a letter to create a MOMonomial

    >>> a = MOnumber(2)
    >>> b = MOstr('x')
    >>> multiply(a, b)
    <MOMonomial 2x>
    >>> a = MOFraction(1, 5)
    >>> multiply(a, b)
    <MOMonomial 1 / 5 * x>
    """
    return MOMonomial(left, right)


@multiply.register(MOstr, (MOnumber, MOFraction))
def mostr_moscalar(left, right):
    """ Multiply a scalar with a letter to create a MOMonomial

    >>> a = MOstr('x')
    >>> b = MOnumber(2)
    >>> multiply(a, b)
    <MOMonomial 2x>
    >>> b = MOFraction(1, 5)
    >>> multiply(a, b)
    <MOMonomial 1 / 5 * x>
    """
    return MOMonomial(right, left)


@multiply.register((MOnumber, MOFraction), MOstrPower)
def moscalar_mostrpower(left, right):
    """ Multiply a scalar with a MOstrPower

    >>> a = MOnumber(4)
    >>> x = MOstrPower('x', 4)
    >>> multiply(a, x)
    <MOMonomial 4x^4>

    """
    return MOMonomial(left, right)


@multiply.register(MOstrPower, (MOnumber, MOFraction))
def mostrpower_moscalar(left, right):
    """ Multiply a MOstrPower with a scalar

    >>> a = MOnumber(4)
    >>> x = MOstrPower('x', 4)
    >>> multiply(x, a)
    <MOMonomial 4x^4>

    """
    return MOMonomial(right, left)


# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
