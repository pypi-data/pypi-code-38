#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 lafrite <lafrite@Poivre>
#
# Distributed under terms of the MIT license.

from mapytex.calculus.core.tree import Tree
from . import MO, MOstr
from .mo import Molecule
from .exceptions import MOError
from .monomial import MOMonomial, MOstrPower

__all__ = ["MOpolynomial"]


class MOpolynomial(Molecule):

    """ MO polynomial"""

    MAINOP = "+"

    def __init__(self, variable, coefs):
        """ Initiate a MOpolynomial

        :param variable: variable of the monomial (a MOstr or later a MOSqrt)
        :param coefs: dictionnary {deg: coef} or a list [coef0, coef1...]

        :example:
        >>> MOpolynomial('x', [1, 2, 3])
        <MOpolynomial 3x^2 + 2x + 1>
        >>> MOpolynomial('x', [1, 0, 3])
        <MOpolynomial 3x^2 + 1>
        >>> MOpolynomial('x', {0: 1, 1: 2, 2: 3})
        <MOpolynomial 3x^2 + 2x + 1>
        >>> MOpolynomial('x', {0: 1, 3: 4})
        <MOpolynomial 4x^3 + 1>
        >>> MOpolynomial('x', {0: 1, 3: 1})
        <MOpolynomial x^3 + 1>

        """
        _variable = MO.factory(variable)
        if not isinstance(_variable, MOstr):
            raise MOError("The variable of a monomial should be convertible into MOstr")
        self._variable = _variable

        if isinstance(coefs, dict):
            _coefs = {
                MO.factory(d): MO.factory(c) for (d, c) in coefs.items() if c != 0
            }
        elif isinstance(coefs, list):
            _coefs = {
                MO.factory(d): MO.factory(c) for (d, c) in enumerate(coefs) if c != 0
            }
        else:
            raise TypeError("Coefs needs to be a dictionnary or a list")
        self._coefs = _coefs

        monomials = {}
        for deg, coef in self._coefs.items():
            if deg == 0:
                monomials[deg] = coef
            elif deg == 1 and coef == 1:
                monomials[deg] = MOstr(self._variable)
            elif coef == 1:
                monomials[deg] = MOstrPower(self._variable, deg)
            else:
                monomials[deg] = MOMonomial(coef, self._variable, deg)

        self._monomials = monomials

        tree = Tree.from_list("+", list(self._monomials.values())[::-1])
        Molecule.__init__(self, tree)

    @property
    def variable(self):
        return self._variable

    @property
    def degree(self):
        """
        Maximum degree of its coefficient

        :example:
        >>> p = MOpolynomial('x', [1, 2, 3])
        >>> p.degree
        2
        >>> p = MOpolynomial('x', {0: 1, 3: 4})
        >>> p.degree
        3

        """
        return self.power.value

    @property
    def power(self):
        """
        Maximum degree of its coefficient

        :example:
        >>> p = MOpolynomial('x', [1, 2, 3])
        >>> p.power
        <MOnumber 2>
        >>> p = MOpolynomial('x', {0: 1, 3: 4})
        >>> p.power
        <MOnumber 3>

        """
        return max(self._coefs.keys())

    @property
    def coefficients(self):
        return self._coefs

    @property
    def monomials(self):
        """ Return dictionnary with degree in keys and monomial in value

        :example:
        >>> p = MOpolynomial('x', [1, 2, 3])
        >>> p.monomials
        {<MOnumber 0>: <MOnumber 1>, <MOnumber 1>: <MOMonomial 2x>, <MOnumber 2>: <MOMonomial 3x^2>}
        >>> p.monomials.values()
        dict_values([<MOnumber 1>, <MOMonomial 2x>, <MOMonomial 3x^2>])
        """
        return self._monomials


# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
