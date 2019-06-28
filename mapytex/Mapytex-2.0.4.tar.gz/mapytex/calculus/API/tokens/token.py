#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 lafrite <lafrite@Poivre>
#
# Distributed under terms of the MIT license.

"""
Tokens: practical envelop of math object

"""
from ..renders import renders


class Token(object):

    """ Token: practical envelop of an math object """

    RENDER = "txt"

    def __init__(self, mo, name="", ancestor=None):
        self._mo = mo
        self.name = name
        self._mathtype = None
        self._ancestor = ancestor

    @classmethod
    def random(cls):
        raise NotImplemented

    def explain(self):
        """ Yield every calculus step which have lead to self
        
        :example:
        >>> from mapytex.calculus.API import Expression
        >>> e = Expression.from_str("2+3*4")
        >>> f = e.simplify()
        >>> f
        <Integer 14>
        >>> for s in f.explain():
        ...     print(s)
        2 + 3 * 4
        2 + 12
        14
        """
        try:
            yield from self._ancestor.explain()
            yield self
        except AttributeError:
            yield self

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.__txt__}>"

    def __str__(self):
        return renders[self.RENDER](self._mo)

    @property
    def __txt__(self):
        return self._mo.__txt__

    @property
    def __tex__(self):
        return self._mo.__tex__

    def _operate(self, other, operation):
        """ Make a operation between 2 Tokens, 
        a Token and en Expression ora
        a Token an a builtin type
        """
        from ..expression import Expression
        from ...core import Tree
        from . import factory

        if not isinstance(other, Token):
            _other = factory(other)
        else:
            _other = other
        tree = Tree(operation, self._mo, _other._mo)
        return Expression(tree).simplify()

    def __add__(self, other):
        """ Adding 2 Tokens or a Token and a Expression

        :example:
        >>> from .number import Integer 
        >>> a = Integer(3)
        >>> b = Integer(7)
        >>> c = a + b
        >>> c
        <Integer 10>
        >>> for i in c.explain():
        ...    print(i)
        3 + 7
        10
        >>> from .number import Fraction 
        >>> a = Fraction("4/3")
        >>> b = Integer(7)
        >>> c = a + b
        >>> c
        <Fraction 25 / 3>
        >>> for i in c.explain():
        ...    print(i)
        4 / 3 + 7
        4 / 3 + 7 / 1
        4 / 3 + (7 * 3) / (1 * 3)
        4 / 3 + 21 / 3
        (4 + 21) / 3
        25 / 3
        """
        return self._operate(other, "+")

    def __mul__(self, other):
        """ Multiply 2 Tokens or a Token and a Expression

        :example:
        >>> from .number import Integer 
        >>> a = Integer(3)
        >>> b = Integer(7)
        >>> c = a * b
        >>> c
        <Integer 21>
        >>> for i in c.explain():
        ...    print(i)
        3 * 7
        21
        >>> from .number import Fraction 
        >>> a = Fraction("4/3")
        >>> b = Integer(7)
        >>> c = a * b
        >>> c
        <Fraction 28 / 3>
        >>> for i in c.explain():
        ...    print(i)
        4 / 3 * 7
        (4 * 7) / 3
        28 / 3
        """
        return self._operate(other, "*")

    def __truediv__(self, other):
        """ Divising 2 Tokens or a Token and a Expression

        :example:
        >>> from .number import Integer 
        >>> a = Integer(3)
        >>> b = Integer(7)
        >>> c = a / b
        >>> c
        <Fraction 3 / 7>
        >>> for i in c.explain():
        ...    print(i)
        3 / 7
        >>> from .number import Fraction 
        >>> a = Fraction("4/3")
        >>> b = Integer(7)
        >>> c = a / b
        >>> c
        <Fraction 4 / 21>
        >>> for i in c.explain():
        ...    print(i)
        4 / 3 / 7
        4 / 3 * 1 / 7
        (4 * 1) / (3 * 7)
        4 / 21
        """
        return self._operate(other, "/")


# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
