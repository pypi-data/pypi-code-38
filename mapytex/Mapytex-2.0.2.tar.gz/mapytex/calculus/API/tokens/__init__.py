#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 lafrite <lafrite@Poivre>
#
# Distributed under terms of the MIT license.

"""
Tokens represents MathObject at API level

"""
from ...core.MO import MO, MOnumber, MOstr
from ...core.MO.fraction import MOFraction
from ...core.MO.monomial import MOstrPower, MOMonomial
from ...core.MO.polynomial import MOpolynomial
from decimal import Decimal as _Decimal

from .number import Integer, Decimal, Fraction
from .polynomial import Polynomial, Linear, Quadratic

__all__ = ["factory"]


def factory(exp, name="", ancestor=None):
    """ Transform a Expression with on MathObject (from core) to a appropriate token (from API)

    :example:
    >>> from ..expression import Expression
    >>> a = Expression(MOnumber(2))
    >>> factory(a)
    <Integer 2>
    >>> a = Expression(MOnumber(2.5))
    >>> factory(a)
    <Decimal 2.5>
    >>> a = Expression(MOFraction(2, 5))
    >>> factory(a)
    <Fraction 2 / 5>
    >>> a = Expression(MOstr('x'))
    >>> factory(a)
    <Linear x>
    >>> a = Expression(MOstrPower('x', 2))
    >>> factory(a)
    <Quadratic x^2>
    >>> a = Expression(MOstrPower('x', 3))
    >>> factory(a)
    <Polynomial x^3>
    >>> a = Expression(MOMonomial(3, 'x', 1))
    >>> factory(a)
    <Linear 3x>
    >>> a = Expression(MOMonomial(3, 'x', 2))
    >>> factory(a)
    <Quadratic 3x^2>
    >>> a = Expression(MOMonomial(3, 'x', 3))
    >>> factory(a)
    <Polynomial 3x^3>
    """
    mo = exp._tree
    if not isinstance(mo, MO):
        raise TypeError(f"Can't build Token from not computed Expression (got {mo})")

    if isinstance(mo, MOnumber):
        if isinstance(mo.value, int):
            return Integer.from_mo(mo, name, ancestor)
        elif isinstance(mo.value, _Decimal):
            return Decimal.from_mo(mo, name, ancestor)

        raise TypeError(f"Can't build from MOnumber ({mo}) neither int nor decimal")

    elif isinstance(mo, MOFraction):
        if isinstance(mo._denominator, MOnumber) and isinstance(
            mo._numerator, MOnumber
        ):
            return Fraction.from_mo(mo, name, ancestor)

        raise TypeError(
            f"Can't build from MOFraction ({mo}) numerator and denominator are not MOnumber"
        )

    elif isinstance(mo, (MOstr, MOstrPower, MOMonomial, MOpolynomial)):
        if not isinstance(mo._variable, (MOstr, str)):
            raise TypeError(
                f"Can't build Polynom over something else than a letter (got {mo._variable})"
            )
        if (
            isinstance(mo, MOstr)
            or (isinstance(mo, MOMonomial) and mo.power.value == 1)
            or (isinstance(mo, MOpolynomial) and mo.power.value == 1)
        ):
            return Linear.from_mo(mo, name, ancestor)
        elif (
            (isinstance(mo, MOstrPower) and mo.power.value == 2)
            or (isinstance(mo, MOMonomial) and mo.power.value == 2)
            or (isinstance(mo, MOpolynomial) and mo.power.value == 2)
        ):
            return Quadratic.from_mo(mo, name, ancestor)
        else:
            return Polynomial.from_mo(mo, name, ancestor)

    else:
        raise TypeError(f"{type(mo)} is unknown MathObject")


# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
