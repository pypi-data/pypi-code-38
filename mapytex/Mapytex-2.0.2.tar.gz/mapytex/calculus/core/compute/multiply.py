#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 lafrite <lafrite@Poivre>
#
# Distributed under terms of the MIT license.

"""
Multiply MO
"""

from multipledispatch import Dispatcher
from ..tree import Tree
from ..MO import MO, MOnumber, MOstr
from ..MO.fraction import MOFraction
from ..MO.monomial import MOstrPower, MOMonomial
from ..MO.polynomial import MOpolynomial
from .filters import special_case

multiply_doc = """ Multiply MOs

:param left: left MO
:param right: right MO
:returns: Tree or MO

"""

multiply = Dispatcher("multiply", doc=multiply_doc)


def multiply_filter(left, right):
    """ Automatic multiply on MO

    :param left: MO
    :param right: MO
    :returns: MO if it is a special case, nothing other wise

    >>> a = MOnumber(1)
    >>> b = MOFraction(1, 2)
    >>> multiply(a, b)
    <MOFraction 1 / 2>
    >>> multiply(b, a)
    <MOFraction 1 / 2>
    >>> a = MOnumber(0)
    >>> b = MOFraction(1, 2)
    >>> multiply(a, b)
    <MOnumber 0>
    """
    try:
        if left == 0:
            return left
    except TypeError:
        pass
    try:
        if right == 0:
            return right
    except TypeError:
        pass

    try:
        if left == 1:
            return right
    except TypeError:
        pass
    try:
        if right == 1:
            return left
    except TypeError:
        pass


@multiply.register(MOnumber, MOnumber)
@special_case(multiply_filter)
def monumber_monumber(left, right):
    """ Simply multiply values

    >>> a = MOnumber(4)
    >>> b = MOnumber(6)
    >>> multiply(a, b)
    <MOnumber 24>

    """
    return MO.factory(left.value * right.value)


@multiply.register(MOnumber, MOFraction)
@special_case(multiply_filter)
def monumber_mofraction(left, right):
    """ Return division Tree with on the numertor MOnumber times numerator of MOFraction

    >>> a = MOnumber(4)
    >>> b = MOFraction(6, 5)
    >>> print(multiply(a, b))
    /
     > *
     | > 4
     | > 6
     > 5
    >>> b = MOFraction(6, 5, True)
    >>> print(multiply(a, b))
    /
     > *
     | > 4
     | > -
     | | > None
     | | > 6
     > 5

    """
    num = Tree("*", left, right.numerator)
    return Tree("/", num, right._denominator)


@multiply.register(MOFraction, MOnumber)
@special_case(multiply_filter)
def mofraction_monumber(left, right):
    """ Return division Tree with on the numertor MOnumber times numerator of MOFraction

    >>> a = MOFraction(6, 5)
    >>> b = MOnumber(4)
    >>> print(multiply(a, b))
    /
     > *
     | > 6
     | > 4
     > 5
    """
    num = Tree("*", left.numerator, right)
    return Tree("/", num, left._denominator)


@multiply.register(MOFraction, MOFraction)
@special_case(multiply_filter)
def mofraction_mofraction(left, right):
    """ Multiply two mofractions (numertors together and denominators together)

    >>> a = MOFraction(1, 5)
    >>> b = MOFraction(4, 5)
    >>> print(multiply(a, b))
    /
     > *
     | > 1
     | > 4
     > *
     | > 5
     | > 5
    """
    num = Tree("*", left.numerator, right.numerator)
    denom = Tree("*", left.denominator, right.denominator)
    return Tree("/", num, denom)


@multiply.register((MOnumber, MOFraction), MOMonomial)
@special_case(multiply_filter)
def moscalar_monomonial(left, right):
    """ Multiply a scalar with a monomial

    >>> a = MOnumber(4)
    >>> x = MOstrPower('x', 4)
    >>> b = MOMonomial(5, x) 
    >>> print(multiply(a, b))
    *
     > *
     | > 4
     | > 5
     > x^4

    """
    coefficient = Tree("*", left, right.coefficient)
    return Tree("*", coefficient, right.strpower)


@multiply.register(MOMonomial, (MOnumber, MOFraction))
@special_case(multiply_filter)
def monomonial_moscalar(left, right):
    """ Multiply a momonial with a scalar

    >>> x = MOstrPower('x', 4)
    >>> a = MOMonomial(5, x) 
    >>> b = MOnumber(4)
    >>> print(multiply(a, b))
    *
     > *
     | > 4
     | > 5
     > x^4

    """
    coefficient = Tree("*", right, left.coefficient)
    return Tree("*", coefficient, left.strpower)


@multiply.register(MOstr, MOstrPower)
@special_case(multiply_filter)
def mostr_mostrpower(left, right):
    """ Multiply a MOstr and a MOstrPower

    >>> a = MOstr('x')
    >>> b = MOstrPower('x', 4)
    >>> multiply(a, b)
    <MOstrPower x^5>
    >>> a = MOstr('x')
    >>> b = MOstrPower('y', 4)
    >>> multiply(a, b)
    Traceback (most recent call last):
        ...
    NotImplementedError: Can't multiply MOstr and MOstrPower if they don'thave same variable (got x and y)
    """
    if left.variable != right.variable:
        raise NotImplementedError(
            "Can't multiply MOstr and MOstrPower if they don't"
            f"have same variable (got {left.variable} and {right.variable})"
        )
    return MOstrPower(left.variable, right.power.value + 1)


@multiply.register(MOstrPower, MOstr)
@special_case(multiply_filter)
def mostr_mostrpower(left, right):
    """ Multiply a MOstr and a MOstrPower

    >>> a = MOstrPower('x', 4)
    >>> b = MOstr('x')
    >>> multiply(a, b)
    <MOstrPower x^5>
    >>> a = MOstrPower('y', 4)
    >>> b = MOstr('x')
    >>> multiply(a, b)
    Traceback (most recent call last):
        ...
    NotImplementedError: Can't multiply MOstr and MOstrPower if they don'thave same variable (got x and y)
    """
    if left.variable != right.variable:
        raise NotImplementedError(
            "Can't multiply MOstr and MOstrPower if they don't"
            f"have same variable (got {left.variable} and {right.variable})"
        )
    return MOstrPower(left.variable, left.power.value + 1)


@multiply.register(MOstr, MOstr)
@special_case(multiply_filter)
def mostr_mostr(left, right):
    """ Multiply a MOstr and a MOstr

    :example:
    >>> a = MOstr('x')
    >>> b = MOstr('x')
    >>> multiply(a, b)
    <MOstrPower x^2>
    >>> a = MOstr('y')
    >>> b = MOstr('x')
    >>> multiply(a, b)
    Traceback (most recent call last):
        ...
    NotImplementedError: Can't multiply MOstr and MOstr if they don'thave same variable (got y and x)
    """
    if left.variable != right.variable:
        raise NotImplementedError(
            "Can't multiply MOstr and MOstr if they don't"
            f"have same variable (got {left.variable} and {right.variable})"
        )
    return MOstrPower(left.variable, 2)


@multiply.register(MOstrPower, MOstrPower)
@special_case(multiply_filter)
def mostr_mostrpower(left, right):
    """ Multiply a MOstrPower and a MOstrPower

    >>> a = MOstrPower('x', 2)
    >>> b = MOstrPower('x', 4)
    >>> print(multiply(a, b))
    ^
     > x
     > +
     | > 2
     | > 4
    >>> a = MOstrPower('x', 2)
    >>> b = MOstrPower('y', 4)
    >>> multiply(a, b)
    Traceback (most recent call last):
        ...
    NotImplementedError: Can't multiply MOstrPower and MOstrPower if they don'thave same variable (got x and y)
    """
    if left.variable != right.variable:
        raise NotImplementedError(
            "Can't multiply MOstrPower and MOstrPower if they don't"
            f"have same variable (got {left.variable} and {right.variable})"
        )
    power = Tree("+", left.power, right.power)
    return Tree("^", left.variable, power)


@multiply.register(MOstrPower, MOMonomial)
@special_case(multiply_filter)
def mostrpower_momonomial(left, right):
    """ Multiply a MOstrPower and a MOMonomial

    >>> a = MOstrPower('x', 2)
    >>> b = MOMonomial(2, 'x', 4)
    >>> print(multiply(a, b))
    *
     > 2
     > ^
     | > x
     | > +
     | | > 2
     | | > 4
    >>> a = MOstrPower('x', 2)
    >>> b = MOMonomial(2, 'y', 4)
    >>> multiply(a, b)
    Traceback (most recent call last):
        ...
    NotImplementedError: Can't multiply MOstrPower and Monomial if they don'thave same variable (got x and y)
    """
    if left.variable != right.variable:
        raise NotImplementedError(
            "Can't multiply MOstrPower and Monomial if they don't"
            f"have same variable (got {left.variable} and {right.variable})"
        )
    power = Tree("+", left.power, right.power)
    monome = Tree("^", left.variable, power)
    return Tree("*", right.coefficient, monome)


@multiply.register(MOMonomial, MOstrPower)
@special_case(multiply_filter)
def momonomial_mostr(left, right):
    """ Multiply a MOMonomial and a MOstrPower

    >>> a = MOMonomial(2, 'x', 4)
    >>> b = MOstrPower('x', 2)
    >>> print(multiply(a, b))
    *
     > 2
     > ^
     | > x
     | > +
     | | > 4
     | | > 2
    >>> a = MOMonomial(2, 'y', 4)
    >>> b = MOstrPower('x', 2)
    >>> multiply(a, b)
    Traceback (most recent call last):
        ...
    NotImplementedError: Can't multiply MOstrPower and Monomial if they don'thave same variable (got y and x)

    """
    if left.variable != right.variable:
        raise NotImplementedError(
            "Can't multiply MOstrPower and Monomial if they don't"
            f"have same variable (got {left.variable} and {right.variable})"
        )
    power = Tree("+", left.power, right.power)
    monome = Tree("^", left.variable, power)
    return Tree("*", left.coefficient, monome)


@multiply.register(MOstr, MOMonomial)
@special_case(multiply_filter)
def mostr_momonomial(left, right):
    """ Multiply a MOstr and a MOMonomial

    >>> a = MOstr('x')
    >>> b = MOMonomial(2, 'x', 4)
    >>> print(multiply(a, b))
    2x^5
    >>> a = MOstr('x')
    >>> b = MOMonomial(2, 'y', 4)
    >>> multiply(a, b)
    Traceback (most recent call last):
        ...
    NotImplementedError: Can't multiply MOstr and Monomial if they don'thave same variable (got x and y)
    """
    if left.variable != right.variable:
        raise NotImplementedError(
            "Can't multiply MOstr and Monomial if they don't"
            f"have same variable (got {left.variable} and {right.variable})"
        )
    return MOMonomial(right.coefficient, right.variable, right.power.value + 1)


@multiply.register(MOMonomial, MOstr)
@special_case(multiply_filter)
def momonomial_mostr(left, right):
    """ Multiply a MOMonomial and a MOstr

    >>> a = MOMonomial(2, 'x', 4)
    >>> b = MOstr('x')
    >>> print(multiply(a, b))
    2x^5
    >>> a = MOMonomial(2, 'y', 4)
    >>> b = MOstr('x')
    >>> multiply(a, b)
    Traceback (most recent call last):
        ...
    NotImplementedError: Can't multiply MOstr and Monomial if they don'thave same variable (got y and x)

    """
    if left.variable != right.variable:
        raise NotImplementedError(
            "Can't multiply MOstr and Monomial if they don't"
            f"have same variable (got {left.variable} and {right.variable})"
        )
    return MOMonomial(left.coefficient, left.variable, left.power.value + 1)


@multiply.register(MOMonomial, MOMonomial)
@special_case(multiply_filter)
def momonomial_momonomial(left, right):
    """ Multiply a MOMonomial and a MOMonomial

    >>> a = MOMonomial(2, 'x', 4)
    >>> b = MOMonomial(3, 'x', 2)
    >>> print(multiply(a, b))
    *
     > *
     | > 2
     | > 3
     > ^
     | > x
     | > +
     | | > 4
     | | > 2
    >>> a = MOMonomial(2, 'y', 4)
    >>> b = MOMonomial(3, 'x', 2)
    >>> multiply(a, b)
    Traceback (most recent call last):
        ...
    NotImplementedError: Can't multiply MOMonomial and Monomial if they don'thave same variable (got y and x)

    """
    if left.variable != right.variable:
        raise NotImplementedError(
            "Can't multiply MOMonomial and Monomial if they don't"
            f"have same variable (got {left.variable} and {right.variable})"
        )
    powers = Tree("+", left.power, right.power)
    monome = Tree("^", left.variable, powers)
    coefs = Tree("*", left.coefficient, right.coefficient)
    return Tree("*", coefs, monome)


@multiply.register((MOnumber, MOFraction, MOstr, MOstrPower, MOMonomial), MOpolynomial)
@special_case(multiply_filter)
def lotsmo_mopolynomial(left, right):
    """ Multiply a scalar and a MOMonomial

    >>> a = MOnumber(2)
    >>> b = MOpolynomial('x', [1, 2, 3])
    >>> print(multiply(a, b))
    +
     > *
     | > 2
     | > 3x^2
     > +
     | > *
     | | > 2
     | | > 2x
     | > *
     | | > 2
     | | > 1

    >>> a = MOFraction(1, 5)
    >>> b = MOpolynomial('x', [1, 2, 3])
    >>> print(multiply(a, b))
    +
     > *
     | > 1 / 5
     | > 3x^2
     > +
     | > *
     | | > 1 / 5
     | | > 2x
     | > *
     | | > 1 / 5
     | | > 1


    >>> a = MOstr("x")
    >>> b = MOpolynomial('x', [1, 2, 3])
    >>> print(multiply(a, b))
    +
     > *
     | > x
     | > 3x^2
     > +
     | > *
     | | > x
     | | > 2x
     | > *
     | | > x
     | | > 1

    >>> a = MOstrPower("x", 2)
    >>> b = MOpolynomial('x', [1, 2, 3])
    >>> print(multiply(a, b))
    +
     > *
     | > x^2
     | > 3x^2
     > +
     | > *
     | | > x^2
     | | > 2x
     | > *
     | | > x^2
     | | > 1

    >>> a = MOMonomial(3, "x", 2)
    >>> b = MOpolynomial('x', [1, 2, 3])
    >>> print(multiply(a, b))
    +
     > *
     | > 3x^2
     | > 3x^2
     > +
     | > *
     | | > 3x^2
     | | > 2x
     | > *
     | | > 3x^2
     | | > 1


    """
    coefs = [Tree("*", left, monom) for monom in list(right.monomials.values())[::-1]]
    return Tree.from_list("+", coefs)


@multiply.register(MOpolynomial, (MOnumber, MOFraction, MOstr, MOstrPower, MOMonomial))
@special_case(multiply_filter)
def mopolynomial_lotsmo(left, right):
    """ Multiply a MOpolynomial with nearly everything

    >>> a = MOpolynomial('x', [1, 2, 3])
    >>> b = MOnumber(2)
    >>> print(multiply(a, b))
    +
     > *
     | > 3x^2
     | > 2
     > +
     | > *
     | | > 2x
     | | > 2
     | > *
     | | > 1
     | | > 2

    >>> a = MOpolynomial('x', [1, 2, 3])
    >>> b = MOFraction(1, 5)
    >>> print(multiply(a, b))
    +
     > *
     | > 3x^2
     | > 1 / 5
     > +
     | > *
     | | > 2x
     | | > 1 / 5
     | > *
     | | > 1
     | | > 1 / 5


    >>> a = MOpolynomial('x', [1, 2, 3])
    >>> b = MOstr("x")
    >>> print(multiply(a, b))
    +
     > *
     | > 3x^2
     | > x
     > +
     | > *
     | | > 2x
     | | > x
     | > *
     | | > 1
     | | > x

    >>> a = MOpolynomial('x', [1, 2, 3])
    >>> b = MOstrPower("x", 2)
    >>> print(multiply(a, b))
    +
     > *
     | > 3x^2
     | > x^2
     > +
     | > *
     | | > 2x
     | | > x^2
     | > *
     | | > 1
     | | > x^2


    >>> a = MOpolynomial('x', [1, 2, 3])
    >>> b = MOMonomial(3, "x", 2)
    >>> print(multiply(a, b))
    +
     > *
     | > 3x^2
     | > 3x^2
     > +
     | > *
     | | > 2x
     | | > 3x^2
     | > *
     | | > 1
     | | > 3x^2

    """
    coefs = [Tree("*", monom, right) for monom in list(left.monomials.values())[::-1]]
    return Tree.from_list("+", coefs)


@multiply.register(MOpolynomial, MOpolynomial)
@special_case(multiply_filter)
def mopolynomial_mopolynomial(left, right):
    """ Multiply 2 MOpolynomial

    >>> a = MOpolynomial('x', [1, 2, 3])
    >>> b = MOpolynomial('x', [4, 5])
    >>> print(multiply(a, b))
    +
     > +
     | > *
     | | > 3x^2
     | | > 5x
     | > +
     | | > *
     | | | > 3x^2
     | | | > 4
     | | > *
     | | | > 2x
     | | | > 5x
     > +
     | > *
     | | > 2x
     | | > 4
     | > +
     | | > *
     | | | > 1
     | | | > 5x
     | | > *
     | | | > 1
     | | | > 4

    """
    coefs = [
        Tree("*", l_monom, r_monom)
        for l_monom in list(left.monomials.values())[::-1]
        for r_monom in list(right.monomials.values())[::-1]
    ]
    return Tree.from_list("+", coefs)


# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
