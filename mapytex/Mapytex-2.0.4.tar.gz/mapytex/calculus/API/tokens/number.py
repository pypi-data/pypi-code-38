#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 lafrite <lafrite@Poivre>
#
# Distributed under terms of the MIT license.

"""
Tokens representing interger and decimal

"""
from decimal import Decimal as _Decimal
from .token import Token
from ...core.arithmetic import gcd
from ...core.random.int_gene import filter_random
from ...core.MO import MO, MOnumber
from ...core.MO.fraction import MOFraction

__all__ = ["Integer", "Decimal"]


class Integer(Token):

    """ Token representing a integer 
    
    :example:
    >>> Integer(4)
    <Integer 4>
    >>> a = MOnumber(4)
    >>> Integer.from_mo(a)
    <Integer 4>
    
    """

    def __init__(self, a, name="", ancestor=None):
        if not isinstance(a, MO):
            if not isinstance(a, int):
                raise TypeError
            mo = MOnumber(a)
        else:
            mo = a

        Token.__init__(self, mo, name, ancestor)
        self._mathtype = "entier"

    @classmethod
    def from_mo(cls, mo, name="", ancestor=None):
        if not isinstance(mo, MOnumber):
            raise TypeError
        if not isinstance(mo.value, int):
            raise TypeError

        return cls(mo, name, ancestor)

    @classmethod
    def random(
        cls, name="", min_value=-10, max_value=10, rejected=[0, 1], accept_callbacks=[]
    ):
        """ Generate a random Integer

        :param name: name of the Integer
        :param min_value: minimum value
        :param max_value: maximum value
        :param rejected: rejected values
        :param accept_callbacks: list of function for value acceptation

        """
        candidate = filter_random(min_value, max_value, rejected, accept_callbacks)

        return Integer(candidate, name)


class Decimal(Token):

    """ Token representing a decimal 
    
    :example:
    >>> Decimal("4.3")
    <Decimal 4.3>
    >>> Decimal(3.3)
    <Decimal 3.29999999999999982236431605997495353221893310546875>
    >>> Decimal(_Decimal("2.3"))
    <Decimal 2.3>
    """

    def __init__(self, a, name="", ancestor=None):
        if not isinstance(a, MO):
            if isinstance(a, _Decimal):
                mo = MOnumber(a)
            elif isinstance(a, (str, float)):
                mo = MOnumber(_Decimal(a))
            else:
                raise TypeError
        else:
            mo = a

        self._mathtype = "décimal"
        Token.__init__(self, mo, name, ancestor)

    @classmethod
    def from_mo(cls, mo, name="", ancestor=None):
        if not isinstance(mo, MOnumber):
            raise TypeError
        if not isinstance(mo.value, _Decimal):
            raise TypeError

        return cls(mo, name, ancestor)

    @classmethod
    def random(
        cls,
        name="",
        min_value=-10,
        max_value=10,
        digits=2,
        rejected=[0, 1],
        reject_callbacks=[],
    ):
        """ Generate a random Decimal

        :param name: name of the Integer
        :param min_value: minimum value
        :param max_value: maximum value
        :param digits: digits after comas
        :param rejected: rejected values
        :param reject_callbacks: list of function for value rejection

        """
        conditions = [lambda x: x in rejected] + reject_callbacks

        float_cand = (max_value - min_value) * random() + min_value
        candidate = _Decimal(f"{float_cand:.{digits}f}")
        while any(c(candidate) for c in conditions):
            float_cand = (max_value - min_value) * random() + min_value
            candidate = _Decimal(f"{float_cand:.{digits}f}")

        return Decimal(candidate, name)


class Fraction(Token):

    """ Token representing a fraction

    :example:
    >>> Fraction("3/4")
    <Fraction 3 / 4>
    """

    def __init__(self, a, name="", ancestor=None):
        if not isinstance(a, MO):
            if isinstance(a, str):
                num, denom = a.split("/")
                mo = MOFraction(int(num), int(denom))
            else:
                raise TypeError
        else:
            mo = a

        self._mathtype = "fraction"
        Token.__init__(self, mo, name, ancestor)

    @classmethod
    def from_mo(cls, mo, name="", ancestor=None):
        if not isinstance(mo, MOFraction):
            raise TypeError
        if not isinstance(mo._numerator, MOnumber):
            raise TypeError
        if not isinstance(mo._denominator, MOnumber):
            raise TypeError

        return cls(mo, name, ancestor)

    @classmethod
    def random(
        cls,
        name="",
        fix_num="",
        min_num=-10,
        max_num=10,
        rejected_num=[0],
        accept_num_callbacks=[],
        fix_denom="",
        min_denom=-10,
        max_denom=10,
        rejected_denom=[0, 1, -1],
        accept_denom_callbacks=[],
        irreductible=False,
        not_integer=True,
    ):
        """ Generate a random Fraction

        :param name: Name of the fraction
        :param fix_num: if set, the numerator will get this value
        :param min_num: minimum value for the numerator
        :param max_num: maximum value for the numerator
        :param rejected_num: rejected values for the numerator
        :param accept_num_callbacks: list of function for numerator rejection
        :param fix_denom: if set, the denomerator will get this value
        :param min_denom: minimum value for the denominator
        :param max_denom: maximum value for the denominator
        :param rejected_denom: rejected values for the denominator
        :param accept_denom_callbacks: list of function for denomerator rejection
        :param irreductible: is the generated fraction necessary irreductible
        :param not_integer: can the generated fraction be egal to an interger
        """
        if fix_num == "":
            num = filter_random(min_num, max_num, rejected_num, accept_num_callbacks)
        else:
            num = fix_num

        if fix_denom == "":
            accept_callbacks = accept_denom_callbacks

            if irreductible:

                def prime_with_num(denom):
                    return gcd(num, denom) == 1

                accept_callbacks.append(prime_with_num)
            if not_integer:

                def not_divise_num(denom):
                    return num % denom != 0

                accept_callbacks.append(not_divise_num)

            denom = filter_random(
                min_denom, max_denom, rejected_denom, accept_callbacks
            )
        else:
            denom = fix_denom

        frac = MOFraction(num, denom)
        return cls(frac, name)

    @property
    def numerator(self):
        return self._mo.numerator

    @property
    def denominator(self):
        return self._mo.denominator


# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
