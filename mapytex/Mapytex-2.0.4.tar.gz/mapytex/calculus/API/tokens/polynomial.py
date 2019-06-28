#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 lafrite <lafrite@Poivre>
#
# Distributed under terms of the MIT license.

"""
Tokens representing polynomials functions 

"""
from .token import Token
from ...core.MO import MO

__all__ = ["Polynomial", "Quadratic", "Linear"]


class Polynomial(Token):

    """ Token representing a polynomial """

    def __init__(self, a, name="", ancestor=None):
        if not isinstance(a, MO):
            if isinstance(a, str):
                raise TypeError
            else:
                raise TypeError
        else:
            mo = a

        Token.__init__(self, mo, name, ancestor)
        self._mathtype = "polynome"

    @classmethod
    def from_mo(cls, mo, name="", ancestor=None):

        return cls(mo, name, ancestor)

    @classmethod
    def random(cls):
        raise NotImplemented

    def __setitem__(self, key, item):
        """ Use Polynomial like if they were a dictionnary to set coefficients """
        pass

    def __getitem__(self, key):
        """ Use Polynomial like if they were a dictionnary to get coefficients """
        pass

    def __call__(self, value):
        """ Call a Polynomial to evaluate itself on value """
        pass


class Linear(Polynomial):

    """ Token representing a linear """

    def __init__(self, mo, name="", ancestor=None):

        Polynomial.__init__(self, mo, name, ancestor)
        self._mathtype = "affine"

    @classmethod
    def random(cls):
        raise NotImplemented


class Quadratic(Polynomial):

    """ Token representing a quadratic """

    def __init__(self, mo, name="", ancestor=None):

        Polynomial.__init__(self, mo, name, ancestor)
        self._mathtype = "polynome du 2nd degré"

    @classmethod
    def random(cls):
        raise NotImplemented


# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
