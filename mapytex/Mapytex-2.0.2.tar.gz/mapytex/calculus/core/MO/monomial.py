#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 lafrite <lafrite@Poivre>
#
# Distributed under terms of the MIT license.

from mapytex.calculus.core.tree import Tree
from .mo import Molecule
from . import MO, MOnumber, MOstr
from .exceptions import MOError

__all__ = ["MOMonomial"]


class MOstrPower(Molecule):

    """ Power of a MOstr """

    MAINOP = "^"

    def __init__(self, variable, power):
        """ Initiate a MOstrPower

        :param variable: variable of the monomial (a MOstr or later a MOSqrt)
        :param power: non negative interger (MOnumber type)

        >>> s = MOstrPower("x", 2)
        >>> s
        <MOstrPower x^2>
        >>> print(s)
        x^2
        >>> print(s.__txt__)
        x^2
        >>> print(s.__tex__)
        x^{2}
        >>> MOstrPower(3, 1)
        Traceback (most recent call last):
        ...
        mapytex.calculus.core.MO.exceptions.MOError: The variable of a monomial should be convertible into MOstr
        >>> MOstrPower("x", 0)
        Traceback (most recent call last):
        ...
        mapytex.calculus.core.MO.exceptions.MOError: The power of a MOstrPower should be greater than 1
        >>> MOstrPower("x", 1)
        Traceback (most recent call last):
        ...
        mapytex.calculus.core.MO.exceptions.MOError: The power of a MOstrPower should be greater than 1
        >>> MOstrPower("x", -2)
        Traceback (most recent call last):
        ...
        mapytex.calculus.core.MO.exceptions.MOError: The power of a MOstrPower should be greater than 1
        >>> MOstrPower("x", 2.4)
        Traceback (most recent call last):
        ...
        mapytex.calculus.core.MO.exceptions.MOError: The power of a monomial should be a integer

        """
        _variable = MO.factory(variable)
        if not isinstance(_variable, MOstr):
            raise MOError("The variable of a monomial should be convertible into MOstr")
        self._variable = _variable

        _power = MO.factory(power)
        if power <= 1:
            raise MOError("The power of a MOstrPower should be greater than 1")
        elif not isinstance(_power.content, int):
            raise MOError("The power of a monomial should be a integer")
        self._power = _power

        _tree = Tree("^", self._variable, self._power)

        Molecule.__init__(self, _tree)

    @property
    def coefficients(self):
        """ Dictionnary of coefficients

        :example:
        >>> p = MOstrPower("x", 2)
        >>> p.coefficients
        {2: <MOnumber 1>}
        """

        return {self.power.value: MOnumber(1)}

    @property
    def variable(self):
        return self._variable

    @property
    def power(self):
        """ MO version """
        return self._power

    @property
    def degree(self):
        """ python version """
        return self._power.value

    @property
    def signature(self):
        """ Name of the mo in the API
        
        :example:
        >>> MOstrPower("x", 3).signature
        'monome3'
        >>> MOstrPower("x", 2).signature
        'monome2'
        """
        return f"monome{self.power}"


class MOMonomial(Molecule):

    """ Monomial math object"""

    MAINOP = "*"

    def __init__(self, coefficient, variable, power=1):
        """ Initiate the MOMonomial

        :param coefficient: coefficient of the monomial (a non zero constant)
        :param variable: variable of the monomial (a MOstr, a MOstrPower)
        :param power: degree of the monomial

        >>> x = MOstr('x')
        >>> m = MOMonomial(4, x)
        >>> m
        <MOMonomial 4x>
        >>> print(m)
        4x
        >>> print(m.__txt__)
        4x
        >>> print(m.__tex__)
        4x
        >>> x = MOstrPower('x', 2)
        >>> MOMonomial(4, x)
        <MOMonomial 4x^2>
        >>> m = MOMonomial(4, 'x')
        >>> m
        <MOMonomial 4x>
        >>> print(m)
        4x
        >>> print(m.__txt__)
        4x
        >>> print(m.__tex__)
        4x
        >>> MOMonomial(4, 'x', 1)
        <MOMonomial 4x>
        >>> MOMonomial(4, 'x', 2)
        <MOMonomial 4x^2>
        >>> x2 = MOstrPower('x', 2)
        >>> MOMonomial(4, x2, 3)
        <MOMonomial 4x^6>
        >>> MOMonomial(0, x)
        Traceback (most recent call last):
            ...
        mapytex.calculus.core.MO.exceptions.MOError: The coefficient of a monomial should not be 0
        """
        _coefficient = MO.factory(coefficient)
        if coefficient == 0:
            raise MOError("The coefficient of a monomial should not be 0")
        elif coefficient == 1:
            raise MOError(
                "The coefficient of a monomial should not be 1, it is a MOstrPower or MOstr"
            )
        self._coefficient = _coefficient

        _variable = MO.factory(variable)
        if isinstance(_variable, MOstrPower):
            _power = MO.factory(_variable.power.value * power)
            _variable = _variable.variable
        elif isinstance(_variable, MOstr):
            _power = MO.factory(power)
        else:
            raise MOError(
                f"variable need to be a MOstrPower or a MOstr. Got {type(variable)}."
            )

        self._variable = _variable
        self._power = _power

        try:
            if self._coefficient.value != 1:
                _tree = Tree("*", self._coefficient, self.strpower)
            else:
                _tree = self.strpower
        except AttributeError:
            _tree = Tree("*", self._coefficient, self.strpower)

        Molecule.__init__(self, _tree)

    def __str__(self):
        if self._coefficient != -1:
            return super(MOMonomial, self).__str__()
        else:
            return "- " + self.strpower.__str__()

    @property
    def __txt__(self):
        if self._coefficient != -1:
            return super(MOMonomial, self).__txt__
        else:
            return "- " + self.strpower.__txt__

    @property
    def __tex__(self):
        if self._coefficient != -1:
            return super(MOMonomial, self).__tex__
        else:
            return "- " + self.strpower.__tex__

    @property
    def coefficient(self):
        return self._coefficient

    @property
    def coefficients(self):
        """ Dictionnary of coefficients

        :example:
        >>> p = MOMonomial(3, "x", 2)
        >>> p.coefficients
        {2: <MOnumber 3>}
        """

        return {self.power.value: self._coefficient}

    @property
    def strpower(self):
        if self._power == 1:
            return self.variable
        return MOstrPower(self._variable, self._power)

    @property
    def variable(self):
        return self._variable

    @property
    def power(self):
        return self._power

    @property
    def degree(self):
        return self._power.value

    @property
    def signature(self):
        """ Name of the mo in the API
        
        :example:
        >>> MOMonomial(2, "x").signature
        'monome1'
        >>> MOMonomial(4, "x", 2).signature
        'monome2'
        """
        return f"monome{self.power}"


# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
