#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 lafrite <lafrite@Poivre>
#
# Distributed under terms of the MIT license.

"""
Add MO with typing
"""

from multipledispatch import Dispatcher
from ..tree import Tree
from ..MO import MO, MOnumber, MOstr
from ..MO.monomial import MOstrPower, MOMonomial
from ..MO.polynomial import MOpolynomial
from ..MO.fraction import MOFraction

add_doc = """ Add MOs

:param left: left MO
:param right: right MO
:returns: MO

"""

add = Dispatcher("add", doc=add_doc)


@add.register((MOnumber, MOFraction), MOstr)
def moscalar_mostr(left, right):
    """ add a scalar with a letter to create a MOpolynomial

    >>> a = MOnumber(2)
    >>> b = MOstr('x')
    >>> add(a, b)
    <MOpolynomial x + 2>
    >>> a = MOFraction(1, 5)
    >>> add(a, b)
    <MOpolynomial x + 1 / 5>
    """
    return MOpolynomial(right, [left, 1])


@add.register(MOstr, (MOnumber, MOFraction))
def mostr_moscalar(left, right):
    """ add a scalar with a letter to create a MOpolynomial

    >>> a = MOstr('x')
    >>> b = MOnumber(2)
    >>> add(a, b)
    <MOpolynomial x + 2>
    >>> b = MOFraction(1, 5)
    >>> add(a, b)
    <MOpolynomial x + 1 / 5>
    """
    return MOpolynomial(left, [right, 1])


@add.register((MOnumber, MOFraction), MOstrPower)
def moscalar_mostrpower(left, right):
    """ add a scalar with a letter to create a MOpolynomial

    >>> a = MOnumber(2)
    >>> b = MOstrPower('x', 3)
    >>> add(a, b)
    <MOpolynomial x^3 + 2>
    >>> a = MOFraction(1, 5)
    >>> add(a, b)
    <MOpolynomial x^3 + 1 / 5>
    """
    return MOpolynomial(right.variable, {0: left, right.power: 1})


@add.register(MOstrPower, (MOnumber, MOFraction))
def mostrpower_moscalar(left, right):
    """ add a scalar with a letter to create a MOpolynomial

    >>> a = MOstrPower('x', 3)
    >>> b = MOnumber(2)
    >>> add(a, b)
    <MOpolynomial x^3 + 2>
    >>> b = MOFraction(1, 5)
    >>> add(a, b)
    <MOpolynomial x^3 + 1 / 5>
    """
    return MOpolynomial(left.variable, {0: right, left.power: 1})


@add.register((MOnumber, MOFraction), MOMonomial)
def moscalar_momonomial(left, right):
    """ add a scalar with a MOMonomial to create a MOpolynomial

    >>> a = MOnumber(2)
    >>> b = MOMonomial(3, 'x', 4)
    >>> add(a, b)
    <MOpolynomial 2 + 3x^4>
    >>> a = MOFraction(1, 5)
    >>> add(a, b)
    <MOpolynomial 1 / 5 + 3x^4>
    """
    return MOpolynomial(right.variable, {right.power: right.coefficient, 0: left})


@add.register(MOMonomial, (MOnumber, MOFraction))
def momonial_moscalar(left, right):
    """ add a scalar with a letter to create a MOpolynomial

    >>> a = MOMonomial(3, 'x', 4)
    >>> b = MOnumber(2)
    >>> add(a, b)
    <MOpolynomial 3x^4 + 2>
    >>> b = MOFraction(1, 5)
    >>> add(a, b)
    <MOpolynomial 3x^4 + 1 / 5>

    """
    return MOpolynomial(left.variable, {0: right, left.power: left.coefficient})


@add.register((MOnumber, MOFraction), MOpolynomial)
def moscalar_mopolynomial(left, right):
    """ add a scalar with a MOpolynomial to create a MOpolynomial

    >>> a = MOnumber(2)
    >>> b = MOpolynomial('x', [0, 2, 3])
    >>> add(a, b)
    <MOpolynomial 2 + 3x^2 + 2x>
    >>> a = MOFraction(1, 5)
    >>> add(a, b)
    <MOpolynomial 1 / 5 + 3x^2 + 2x>
    """
    if 0 in right.coefficients.keys():
        raise NotImplementedError(
            f"Polynomial with constant ({right.coefficients[0]}), calculus to do"
        )

    new_coefs = {**right.coefficients}
    #! Need to be add at the end to be printed at the beginning
    new_coefs[0] = left
    return MOpolynomial(right.variable, new_coefs)


@add.register(MOpolynomial, (MOnumber, MOFraction))
def mopolynomial_moscalar(left, right):
    """ add a scalar with a MOpolynomial to create a MOpolynomial

    >>> a = MOpolynomial('x', [0, 2, 3])
    >>> b = MOnumber(2)
    >>> add(a, b)
    <MOpolynomial 3x^2 + 2x + 2>
    >>> b = MOFraction(1, 5)
    >>> add(a, b)
    <MOpolynomial 3x^2 + 2x + 1 / 5>
    """
    if 0 in left.coefficients.keys():
        raise NotImplementedError("Polynomial with constant, calculus to do")

    #! Need to be add at the beginning to be printed at the end
    new_coefs = {0: right}
    new_coefs = {**new_coefs, **left.coefficients}
    return MOpolynomial(left.variable, new_coefs)


@add.register(MOstr, MOstr)
def mostr_mostr(left, right):
    """ add 2 mostr

    >>> a = MOstr('x')
    >>> b = MOstr('x')
    >>> add(a, b)
    <MOMonomial 2x>
    """
    if left != right:
        raise NotImplementedError("Can't add 2 Mostr without same letter")
    return MOMonomial(2, left)


@add.register(MOstr, MOstrPower)
def mostr_mostrpower(left, right):
    """ add a scalar with a letter to create a MOpolynomial

    >>> a = MOstr('x')
    >>> b = MOstrPower('x', 3)
    >>> add(a, b)
    <MOpolynomial x^3 + x>
    >>> b = MOstrPower('x', 2)
    >>> add(a, b)
    <MOpolynomial x^2 + x>
    """
    if left != right.variable:
        raise
    return MOpolynomial(left, {1: 1, right.power: 1})


@add.register(MOstrPower, MOstr)
def mostrpower_mostr(left, right):
    """ add a scalar with a letter to create a MOpolynomial

    >>> a = MOstrPower('x', 3)
    >>> b = MOstr('x')
    >>> add(a, b)
    <MOpolynomial x^3 + x>
    >>> a = MOstrPower('x', 2)
    >>> add(a, b)
    <MOpolynomial x^2 + x>
    """
    if right != left.variable:
        raise
    return MOpolynomial(right, {1: 1, left.power: 1})


@add.register(MOstrPower, MOstrPower)
def mostrpower_mostrpower(left, right):
    """ add 2 mostrpower

    >>> a = MOstrPower('x', 3)
    >>> b = MOstrPower('x', 3)
    >>> add(a, b)
    <MOMonomial 2x^3>
    """
    if left.variable != right.variable:
        raise NotImplementedError("Can't add 2 Mostrpower without same letter")
    if left.power != right.power:
        raise NotImplementedError(
            "Can't add 2 Mostrpower with compute if not same degree"
        )

    return MOMonomial(2, left.variable, left.power)


@add.register(MOstr, MOpolynomial)
def mostr_mopolynomial(left, right):
    """ add a str with a MOpolynomial to create a MOpolynomial

    >>> a = MOstr("x")
    >>> b = MOpolynomial('x', [1, 0, 3])
    >>> add(a, b)
    <MOpolynomial x + 3x^2 + 1>
    """
    if 1 in right.coefficients.keys():
        raise NotImplementedError("Polynomial with no constant, calculus to do")

    new_coefs = {**right.coefficients}
    #! Need to be add at the end to be printed at the beginning
    new_coefs[1] = 1
    return MOpolynomial(right.variable, new_coefs)


@add.register(MOpolynomial, MOstr)
def mopolynomial_mostr(left, right):
    """ add a str with a MOpolynomial to create a MOpolynomial

    >>> a = MOpolynomial('x', [1, 0, 3])
    >>> b = MOstr("x")
    >>> add(a, b)
    <MOpolynomial 3x^2 + 1 + x>
    """
    if 1 in left.coefficients.keys():
        raise NotImplementedError("Polynomial with no constant, calculus to do")

    new_coefs = {1: 1}
    new_coefs = {**new_coefs, **left.coefficients}
    return MOpolynomial(left.variable, new_coefs)


@add.register(MOstrPower, MOpolynomial)
def mostrpower_mopolynomial(left, right):
    """ add a strPower with a MOpolynomial to create a MOpolynomial

    >>> a = MOstrPower("x", 2)
    >>> b = MOpolynomial('x', [1, 2, 0, 4])
    >>> add(a, b)
    <MOpolynomial x^2 + 4x^3 + 2x + 1>
    """
    if left.power in right.coefficients.keys():
        raise NotImplementedError("Degree in common, need to compute")

    new_coefs = {**right.coefficients}
    #! Need to be add at the end to be printed at the beginning
    new_coefs[left.power] = 1
    return MOpolynomial(right.variable, new_coefs)


@add.register(MOpolynomial, MOstrPower)
def mopolynomial_mostrpower(left, right):
    """ add a strPower with a MOpolynomial to create a MOpolynomial

    >>> a = MOpolynomial('x', [1, 2, 0, 4])
    >>> b = MOstrPower("x", 2)
    >>> add(a, b)
    <MOpolynomial 4x^3 + 2x + 1 + x^2>
    """
    if right.power in left.coefficients.keys():
        raise NotImplementedError("Degree in common, need to compute")

    new_coefs = {right.power: 1}
    new_coefs = {**new_coefs, **left.coefficients}
    return MOpolynomial(left.variable, new_coefs)


@add.register(MOMonomial, MOpolynomial)
def momonomial_mopolynomial(left, right):
    """ add a Monomial with a MOpolynomial to create a MOpolynomial

    >>> a = MOMonomial(3, "x", 2)
    >>> b = MOpolynomial('x', [1, 2, 0, 4])
    >>> add(a, b)
    <MOpolynomial 3x^2 + 4x^3 + 2x + 1>
    """
    if left.power in right.coefficients.keys():
        raise NotImplementedError("Degree in common, need to compute")

    new_coefs = {**right.coefficients}
    #! Need to be add at the end to be printed at the beginning
    new_coefs[left.power] = left.coefficient
    return MOpolynomial(right.variable, new_coefs)


@add.register(MOpolynomial, MOMonomial)
def mopolynomial_momonomial(left, right):
    """ add a Monomial with a MOpolynomial to create a MOpolynomial

    >>> a = MOpolynomial('x', [1, 2, 0, 4])
    >>> b = MOMonomial(3, "x", 2)
    >>> add(a, b)
    <MOpolynomial 4x^3 + 2x + 1 + 3x^2>
    """
    if right.power in left.coefficients.keys():
        raise NotImplementedError("Degree in common, need to compute")

    new_coefs = {right.power: right.coefficient}
    new_coefs = {**new_coefs, **left.coefficients}
    return MOpolynomial(left.variable, new_coefs)


@add.register(MOpolynomial, MOpolynomial)
def mopolynomial_mopolynomial(left, right):
    """ add a polynomial with a MOpolynomial to create a MOpolynomial

    >>> a = MOpolynomial('x', [1, 0, 3])
    >>> b = MOpolynomial('x', [0, 2, 0, 4])
    >>> add(a, b)
    <MOpolynomial 3x^2 + 1 + 4x^3 + 2x>
    >>> add(b, a)
    <MOpolynomial 4x^3 + 2x + 3x^2 + 1>
    """
    common_degree = set(left.monomials.keys()).intersection(right.monomials.keys())
    if common_degree:
        raise NotImplementedError("Degree in common, need to compute")

    new_coefs = {**right.coefficients, **left.coefficients}
    return MOpolynomial(right.variable, new_coefs)


@add.register(MOstr, MOMonomial)
def mostr_monomial(left, right):
    """ add a mostr with a MOMonomial to create a MOpolynomial

    >>> a = MOstr('x')
    >>> b = MOMonomial(3, 'x', 4)
    >>> add(a, b)
    <MOpolynomial x + 3x^4>
    """
    if right.power == 1:
        raise NotImplementedError("Monomial is deg 1, need to compute")

    return MOpolynomial(right.variable, {right.power: right.coefficient, 1: 1})


@add.register(MOMonomial, MOstr)
def monomial_mostr(left, right):
    """ add a mostr with a MOMonomial to create a MOpolynomial

    >>> a = MOMonomial(3, 'x', 4)
    >>> b = MOstr('x')
    >>> add(a, b)
    <MOpolynomial 3x^4 + x>
    """
    if left.power == 1:
        raise NotImplementedError("Monomial is deg 1, need to compute")

    return MOpolynomial(left.variable, {1: 1, left.power: left.coefficient})


@add.register(MOstrPower, MOMonomial)
def mostrpower_monomial(left, right):
    """ add a mostrPower with a MOMonomial to create a MOpolynomial

    >>> a = MOstrPower('x', 2)
    >>> b = MOMonomial(3, 'x', 4)
    >>> add(a, b)
    <MOpolynomial x^2 + 3x^4>
    """
    if left.power == right.power:
        raise NotImplementedError(
            "MostrPower and MOMonomial are same degree, need to compute"
        )

    return MOpolynomial(right.variable, {right.power: right.coefficient, left.power: 1})


@add.register(MOMonomial, MOstrPower)
def monomial_mostrpower(left, right):
    """ add a mostrPower with a MOMonomial to create a MOpolynomial

    >>> a = MOMonomial(3, 'x', 4)
    >>> b = MOstrPower('x', 3)
    >>> add(a, b)
    <MOpolynomial 3x^4 + x^3>
    """
    if left.power == right.power:
        raise NotImplementedError(
            "MostrPower and MOMonomial are same degree, need to compute"
        )

    return MOpolynomial(left.variable, {right.power: 1, left.power: left.coefficient})


@add.register(MOMonomial, MOMonomial)
def monomial_momonomial(left, right):
    """ add a moMonomial with a MOMonomial to create a MOpolynomial

    >>> a = MOMonomial(3, 'x', 4)
    >>> b = MOMonomial(2, 'x', 3)
    >>> add(a, b)
    <MOpolynomial 3x^4 + 2x^3>
    """
    if left.power == right.power:
        raise NotImplementedError("MOMonomials are same degree, need to compute")

    return MOpolynomial(
        left.variable, {right.power: right.coefficient, left.power: left.coefficient}
    )


# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
