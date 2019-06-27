#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 lafrite <lafrite@Poivre>
#
# Distributed under terms of the MIT license.

"""
Adding MO
"""

from multipledispatch import Dispatcher
from ..tree import Tree
from ..MO import MO, MOnumber, MOstr
from ..MO.fraction import MOFraction
from ..MO.monomial import MOstrPower, MOMonomial
from ..MO.polynomial import MOpolynomial
from ..arithmetic import lcm
from .filters import special_case

add_doc = """ Adding MOs

:param left: left MO
:param right: right MO
:return: Tree or MO

"""

add = Dispatcher("add", doc=add_doc)


def add_filter(left, right):
    """ Automatic add on MO

    :param left: MO
    :param right: MO
    :returns: MO if it is a special case, nothing other wise

    >>> a = MOnumber(0)
    >>> b = MOFraction(1, 2)
    >>> add(a, b)
    <MOFraction 1 / 2>
    >>> add(b, a)
    <MOFraction 1 / 2>
    """
    try:
        if left == 0:
            return right
    except TypeError:
        pass
    try:
        if right == 0:
            return left
    except TypeError:
        pass
    try:
        if left.variable != right.variable:
            raise NotImplementedError("Can't add 2 polynomes with not same letter")
    except AttributeError:
        pass


@add.register(MOnumber, MOnumber)
@special_case(add_filter)
def monumber_monumber(left, right):
    """ Simply add MO value

    >>> a = MOnumber(4)
    >>> b = MOnumber(6)
    >>> add(a, b)
    <MOnumber 10>

    """
    return MO.factory(left.value + right.value)


@add.register(MOnumber, MOFraction)
@special_case(add_filter)
def monumber_mofraction(left, right):
    """ Return a tree with the MOnumber transformed into a MOFraction

    >>> a = MOnumber(4)
    >>> b = MOFraction(6, 5)
    >>> print(add(a, b))
    +
     > 4 / 1
     > 6 / 5
    """
    left_fraction = MOFraction(left, MOnumber(1))
    return Tree("+", left_fraction, right)


@add.register(MOFraction, MOnumber)
@special_case(add_filter)
def mofraction_monumber(left, right):
    """ Return a tree with the MOnumber transformed into a MOFraction

    >>> a = MOFraction(6, 5)
    >>> b = MOnumber(4)
    >>> print(add(a, b))
    +
     > 6 / 5
     > 4 / 1

    """
    right_fraction = MOFraction(right, MOnumber(1))
    return Tree("+", left, right_fraction)


@add.register(MOFraction, MOFraction)
@special_case(add_filter)
def mofraction_mofraction(left, right):
    """ 3 differents cases:

    Fractions have same denomintor -> add numerator Tree

    >>> a = MOFraction(1, 5)
    >>> b = MOFraction(4, 5)
    >>> print(add(a, b))
    /
     > +
     | > 1
     | > 4
     > 5
    >>> a = MOFraction(1, 5, True)
    >>> b = MOFraction(4, 5)
    >>> print(mofraction_mofraction(a, b))
    /
     > +
     | > -
     | | > None
     | | > 1
     | > 4
     > 5
    >>> a = MOFraction(1, 5)
    >>> b = MOFraction(4, 5, True)
    >>> print(mofraction_mofraction(a, b))
    /
     > +
     | > 1
     | > -
     | | > None
     | | > 4
     > 5

    A denominator is a multiple of the other

    >>> a = MOFraction(1, 2)
    >>> b = MOFraction(1, 4)
    >>> print(mofraction_mofraction(a, b))
    +
     > /
     | > *
     | | > 1
     | | > 2
     | > *
     | | > 2
     | | > 2
     > 1 / 4


    Denominators are coprime

    >>> a = MOFraction(1, 2)
    >>> b = MOFraction(1, 5)
    >>> print(mofraction_mofraction(a, b))
    +
     > /
     | > *
     | | > 1
     | | > 5
     | > *
     | | > 2
     | | > 5
     > /
     | > *
     | | > 1
     | | > 2
     | > *
     | | > 5
     | | > 2
    """
    if left.denominator == right.denominator:
        num = Tree("+", left.numerator, right.numerator)
        return Tree("/", num, left.denominator)

    denom_lcm = lcm(left.denominator.value, right.denominator.value)

    if left.denominator.value == denom_lcm:
        left_frac = left
    else:
        multiply_by = MO.factory(denom_lcm // left.denominator.value)
        left_num = Tree("*", left.numerator, multiply_by)
        left_denom = Tree("*", left.denominator, multiply_by)
        left_frac = Tree("/", left_num, left_denom)

    if right.denominator.value == denom_lcm:
        right_frac = right
    else:
        multiply_by = MO.factory(denom_lcm // right.denominator.value)
        right_num = Tree("*", right.numerator, multiply_by)
        right_denom = Tree("*", right.denominator, multiply_by)
        right_frac = Tree("/", right_num, right_denom)

    return Tree("+", left_frac, right_frac)


@add.register(MOstr, MOstr)
@special_case(add_filter)
def mostr_mostr(left, right):
    """ Add 2 MOstr

    :example:
    >>> a = MOstr("x")
    >>> b = MOstr("x")
    >>> add(a, b)
    <MOMonomial 2x>
    """
    if left != right:
        raise NotImplementedError("Can't add 2 MOstr with not same letter")
    return MOMonomial(2, left)


@add.register(MOstrPower, MOstrPower)
@special_case(add_filter)
def mostrpower_mostrpower(left, right):
    """ Add 2 MOstrPower

    :example:
    >>> a = MOstrPower("x", 2)
    >>> b = MOstrPower("x", 2)
    >>> add(a, b)
    <MOMonomial 2x^2>
    """
    if left.power != right.power:
        raise NotImplementedError("Can't add 2 MOstrPower with not same power")
    return MOMonomial(2, left.variable, left.power)


@add.register((MOnumber, MOFraction), MOpolynomial)
@special_case(add_filter)
def moscalar_mopolynomial(left, right):
    """ Add a scalar to a polynomial

    :example:
    >>> a = MOnumber(1)
    >>> b = MOpolynomial("x", [2, 3, 4])
    >>> print(add(a, b))
    +
     > 4x^2
     > +
     | > 3x
     | > +
     | | > 1
     | | > 2
    """
    if 0 not in right.coefficients.keys():
        raise NotImplementedError("Polynomial with no constant, no calculus to do")

    right_const = right.monomials[0]
    right_top = [mo for deg, mo in right.monomials.items() if deg > 0][::-1]

    adds = right_top + [Tree("+", left, right_const)]
    return Tree.from_list("+", adds)


@add.register(MOpolynomial, (MOnumber, MOFraction))
@special_case(add_filter)
def mopolynomial_moscalar(left, right):
    """ Add a scalar to a polynomial

    :example:
    >>> a = MOpolynomial("x", [2, 3, 4])
    >>> b = MOnumber(1)
    >>> print(add(a, b))
    +
     > 4x^2
     > +
     | > 3x
     | > +
     | | > 2
     | | > 1
    """
    if 0 not in left.coefficients.keys():
        raise NotImplementedError("Polynomial with no constant, no calculus to do")

    left_const = left.monomials[0]
    left_top = [mo for deg, mo in left.monomials.items() if deg > 0][::-1]

    adds = left_top + [Tree("+", left_const, right)]
    return Tree.from_list("+", adds)


@add.register(MOstr, MOpolynomial)
@special_case(add_filter)
def mostr_mopolynomial(left, right):
    """ Add a str to a polynomial

    :example:
    >>> a = MOstr("x")
    >>> b = MOpolynomial("x", [2, 3, 4])
    >>> print(add(a, b))
    +
     > 4x^2
     > +
     | > +
     | | > x
     | | > 3x
     | > 2

    """
    if 1 not in right.coefficients.keys():
        raise NotImplementedError("Polynomial with no constant, no calculus to do")

    right_coef = right.monomials[1]
    add_coefs = Tree("+", left, right_coef)

    right_top = [mo for deg, mo in right.monomials.items() if deg > 1][::-1]
    right_bot = [mo for deg, mo in right.monomials.items() if deg < 1][::-1]

    adds = right_top + [add_coefs] + right_bot

    return Tree.from_list("+", adds)


@add.register(MOpolynomial, MOstr)
@special_case(add_filter)
def mopolynomial_mostr(left, right):
    """ Add a str to a polynomial

    :example:
    >>> a = MOpolynomial("x", [2, 3, 4])
    >>> b = MOstr("x")
    >>> print(add(a, b))
    +
     > 4x^2
     > +
     | > +
     | | > 3x
     | | > x
     | > 2

    """
    if 1 not in left.coefficients.keys():
        raise NotImplementedError("No degree in common")

    left_coef = left.monomials[1]
    add_coefs = Tree("+", left_coef, right)

    left_top = [mo for deg, mo in left.monomials.items() if deg > 1][::-1]
    left_bot = [mo for deg, mo in left.monomials.items() if deg < 1][::-1]

    adds = left_top + [add_coefs] + left_bot

    return Tree.from_list("+", adds)


@add.register(MOstrPower, MOpolynomial)
@special_case(add_filter)
def mostrpower_mopolynomial(left, right):
    """ Add a strpower to a polynomial

    :example:
    >>> a = MOstrPower("x", 2)
    >>> b = MOpolynomial("x", [2, 3, 4])
    >>> print(add(a, b))
    +
     > +
     | > x^2
     | > 4x^2
     > +
     | > 3x
     | > 2

    >>> b = MOpolynomial("x", [2, 3, 4, 5])
    >>> print(add(a, b))
    +
     > +
     | > 5x^3
     | > +
     | | > x^2
     | | > 4x^2
     > +
     | > 3x
     | > 2

    """
    if left.power not in right.coefficients.keys():
        raise NotImplementedError("No degree in common")

    right_mono = right.monomials[left.power]
    add_coefs = Tree("+", left, right_mono)

    right_top = [mo for deg, mo in right.monomials.items() if deg > left.power][::-1]
    right_bot = [mo for deg, mo in right.monomials.items() if deg < left.power][::-1]

    adds = right_top + [add_coefs] + right_bot

    return Tree.from_list("+", adds)


@add.register(MOpolynomial, MOstrPower)
@special_case(add_filter)
def mopolynomial_mostrpower(left, right):
    """ Add a strpower to a polynomial

    :example:
    >>> a = MOpolynomial("x", [2, 3, 4])
    >>> b = MOstrPower("x", 2)
    >>> print(add(a, b))
    +
     > +
     | > 4x^2
     | > x^2
     > +
     | > 3x
     | > 2


    >>> a = MOpolynomial("x", [2, 3, 4, 5])
    >>> print(add(a, b))
    +
     > +
     | > 5x^3
     | > +
     | | > 4x^2
     | | > x^2
     > +
     | > 3x
     | > 2

    """
    if right.power not in left.coefficients.keys():
        raise NotImplementedError("No degree in common")

    left_mono = left.monomials[right.power]
    add_coefs = Tree("+", left_mono, right)

    left_top = [mo for deg, mo in left.monomials.items() if deg > right.power][::-1]
    left_bot = [mo for deg, mo in left.monomials.items() if deg < right.power][::-1]

    adds = left_top + [add_coefs] + left_bot

    return Tree.from_list("+", adds)


@add.register(MOMonomial, MOpolynomial)
@special_case(add_filter)
def momonomial_mopolynomial(left, right):
    """ Add a monomial to a polynomial

    :example:
    >>> a = MOMonomial(10, "x", 2)
    >>> b = MOpolynomial("x", [2, 3, 4])
    >>> print(add(a, b))
    +
     > +
     | > 10x^2
     | > 4x^2
     > +
     | > 3x
     | > 2

    >>> b = MOpolynomial("x", [2, 3, 4, 5])
    >>> print(add(a, b))
    +
     > +
     | > 5x^3
     | > +
     | | > 10x^2
     | | > 4x^2
     > +
     | > 3x
     | > 2

    """
    if left.power not in right.coefficients.keys():
        raise NotImplementedError("No degree in common")

    right_mono = right.monomials[left.power]
    add_coefs = Tree("+", left, right_mono)

    right_top = [mo for deg, mo in right.monomials.items() if deg > left.power][::-1]
    right_bot = [mo for deg, mo in right.monomials.items() if deg < left.power][::-1]

    adds = right_top + [add_coefs] + right_bot

    return Tree.from_list("+", adds)


@add.register(MOpolynomial, MOMonomial)
@special_case(add_filter)
def mopolynomial_momonomial(left, right):
    """ Add a monomial to a polynomial

    :example:
    >>> a = MOpolynomial("x", [2, 3, 4])
    >>> b = MOMonomial(10, "x", 2)
    >>> print(add(a, b))
    +
     > +
     | > 4x^2
     | > 10x^2
     > +
     | > 3x
     | > 2

    >>> a = MOpolynomial("x", [2, 3, 4, 5])
    >>> print(add(a, b))
    +
     > +
     | > 5x^3
     | > +
     | | > 4x^2
     | | > 10x^2
     > +
     | > 3x
     | > 2

    """
    if right.power not in left.coefficients.keys():
        raise NotImplementedError("No degree in common")

    left_mono = left.monomials[right.power]
    add_coefs = Tree("+", left_mono, right)

    left_top = [mo for deg, mo in left.monomials.items() if deg > right.power][::-1]
    left_bot = [mo for deg, mo in left.monomials.items() if deg < right.power][::-1]

    adds = left_top + [add_coefs] + left_bot

    return Tree.from_list("+", adds)


@add.register(MOpolynomial, MOpolynomial)
@special_case(add_filter)
def mopolynomial_mopolynomial(left, right):
    """ Add a polynomial to a polynomial

    :example:
    >>> a = MOpolynomial("x", [2, 3, 4])
    >>> b = MOpolynomial("x", [5, 6, 7])
    >>> print(add(a, b))
    +
     > +
     | > 4x^2
     | > 7x^2
     > +
     | > +
     | | > 3x
     | | > 6x
     | > +
     | | > 2
     | | > 5

    >>> b = MOpolynomial("x", [0, 3, 4])
    >>> print(add(a, b))
    +
     > +
     | > 4x^2
     | > 4x^2
     > +
     | > +
     | | > 3x
     | | > 3x
     | > 2

    >>> b = MOpolynomial("x", [0, 3, 0, 5])
    >>> print(add(a, b))
    +
     > +
     | > 5x^3
     | > 4x^2
     > +
     | > +
     | | > 3x
     | | > 3x
     | > 2

    """
    common_degree = set(left.monomials.keys()).intersection(right.monomials.keys())
    if not common_degree:
        raise NotImplementedError("No degree in common, no calculus to do")

    merge_monomials = {**left.monomials, **right.monomials}
    for deg in common_degree:
        merge_monomials[deg] = Tree("+", left.monomials[deg], right.monomials[deg])

    return Tree.from_list("+", list(merge_monomials.values())[::-1])


@add.register(MOstr, MOMonomial)
@special_case(add_filter)
def mostr_momonomial(left, right):
    """ Add a str to a Monomial

    :example:
    >>> a = MOstr("x")
    >>> b = MOMonomial(2, "x")
    >>> print(add(a, b))
    *
     > +
     | > 1
     | > 2
     > x
    """
    if right.power != 1:
        raise NotImplementedError("Monomial is more than deg 1")
    add_scal = Tree("+", 1, right.coefficient)
    return Tree("*", add_scal, left)


@add.register(MOMonomial, MOstr)
@special_case(add_filter)
def momonomial_mostr(left, right):
    """ Add a str to a Monomial

    :example:
    >>> a = MOMonomial(2, "x")
    >>> b = MOstr("x")
    >>> print(add(a, b))
    *
     > +
     | > 2
     | > 1
     > x
    """
    if left.power != 1:
        raise NotImplementedError("Monomial is more than deg 1")
    add_scal = Tree("+", left.coefficient, 1)
    return Tree("*", add_scal, right)


@add.register(MOstrPower, MOMonomial)
@special_case(add_filter)
def mostrpower_momonomial(left, right):
    """ Add a strpower to a Monomial

    :example:
    >>> a = MOstrPower("x", 2)
    >>> b = MOMonomial(3, "x", 2)
    >>> print(add(a, b))
    *
     > +
     | > 1
     | > 3
     > x^2
    """
    if right.power != left.power:
        raise NotImplementedError("MOs does not have same degree")
    add_scal = Tree("+", 1, right.coefficient)
    return Tree("*", add_scal, left)


@add.register(MOMonomial, MOstrPower)
@special_case(add_filter)
def momonomial_mostrpower(left, right):
    """ Add a strpower to a Monomial

    :example:
    >>> a = MOMonomial(3, "x", 2)
    >>> b = MOstrPower("x", 2)
    >>> print(add(a, b))
    *
     > +
     | > 3
     | > 1
     > x^2
    """
    if left.power != right.power:
        raise NotImplementedError("MOs does not have same degree")
    add_scal = Tree("+", left.coefficient, 1)
    return Tree("*", add_scal, right)


@add.register(MOMonomial, MOMonomial)
@special_case(add_filter)
def momonomial_momonomial(left, right):
    """ Add a Monomial to a Monomial

    :example:
    >>> a = MOMonomial(3, "x", 2)
    >>> b = MOMonomial(4, "x", 2)
    >>> print(add(a, b))
    *
     > +
     | > 3
     | > 4
     > x^2

    """
    if left.power != right.power:
        raise NotImplementedError("MOs does not have same degree")
    add_scal = Tree("+", left.coefficient, right.coefficient)
    return Tree("*", add_scal, right.strpower)


# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
