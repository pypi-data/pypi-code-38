#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 lafrite <lafrite@Poivre>
#
# Distributed under terms of the MIT license.

from decimal import Decimal
from functools import total_ordering
from .exceptions import MOError
from .mo import Atom
from ..coroutine import coroutine, STOOOP


__all__ = ["moify", "MOnumber", "MOstr"]


def moify(token):
    try:
        return MOnumber(token)
    except MOError:
        pass
    try:
        return MOstr(token)
    except MOError:
        return token

@coroutine
def moify_cor(target):
    """ Coroutine which try to convert a parsed token into an MO 

    :example:
    >>> from ..str2 import list_sink
    >>> list2molist = moify_cor(list_sink)
    >>> for i in [-2, "+", "x", "*", Decimal("3.3")]:
    ...    list2molist.send(i)
    >>> list2molist.throw(STOOOP)
    [<MOnumber - 2>, '+', <MOstr x>, '*', <MOnumber 3.3>]

    """
    try:
        target_ = target()
    except TypeError:
        target_ = target

    try:
        while True:
            tok = yield
            target_.send(moify(tok))

    except STOOOP as err:
        yield target_.throw(err)


@total_ordering
class MOnumber(Atom):

    """ Base number math object (int or Decimal)

    :example:
    >>> x = MOnumber(2)
    >>> x
    <MOnumber 2>
    >>> print(x)
    2
    >>> x.__txt__
    '2'
    >>> x.__tex__
    '2'
    """

    def __init__(self, value):
        """ Initiate a number MO

        :example:
        >>> MOnumber(23)
        <MOnumber 23>
        >>> MOnumber(-23)
        <MOnumber - 23>

        As expected there will be trouble with float

        >>> MOnumber(23.3)
        <MOnumber 23.300000000000000710542735760100185871124267578125>

        It will be better to use Decimal

        >>> MOnumber(Decimal("23.3"))
        <MOnumber 23.3>
        >>> MOnumber(Decimal("-23.3"))
        <MOnumber - 23.3>

        MOnumber initialisation is idempotent

        >>> a = MOnumber(23)
        >>> MOnumber(a)
        <MOnumber 23>

        >>> MOnumber("a")
        Traceback (most recent call last):
            ...
        mapytex.calculus.core.MO.exceptions.MOError: ('The value of an MOnumber need to be a int, a float or a Decimal', "(got <class 'str'>)")

        Atoms specific property and methods

        >>> print(a)
        23
        >>> a.value
        23
        >>> a.__txt__
        '23'
        >>> a.__tex__
        '23'
        >>> a._signature
        'scalar'
        """
        if isinstance(value, Atom) and isinstance(value.value, (int, Decimal, float)):
            Atom.__init__(self, value.value)
        elif isinstance(value, (int, Decimal)):
            Atom.__init__(self, value)
        elif isinstance(value, float):
            Atom.__init__(self, Decimal(value))
        else:
            raise MOError(
                "The value of an MOnumber need to be a int, a float or a Decimal",
                f"(got {type(value)})",
            )

        self._signature = "scalar"

    @property
    def __txt__(self):
        """ Txt rendering

        :example:
        >>> MOnumber(3).__txt__
        '3'
        >>> MOnumber(-3).__txt__
        '- 3'
        """
        if self.value >= 0:
            return str(self.value)

        return f"- {abs(self.value)}"

    @property
    def __tex__(self):
        """ Tex rendering

        :example:
        >>> MOnumber(3).__tex__
        '3'
        >>> MOnumber(-3).__tex__
        '- 3'
        """
        if self.value > 0:
            return str(self.value)

        return f"- {abs(self.value)}"

    def __lt__(self, other):
        """ < a MOnumber """
        try:
            return self.value < other.value
        except AttributeError:
            return self.value < other


class MOstr(Atom):

    """ Unknown math object like x or n

    :example:
    >>> x = MOstr('x')
    >>> x
    <MOstr x>
    >>> print(x)
    x
    >>> x.__txt__
    'x'
    >>> x.__tex__
    'x'

    Polynoms properties

    >>> x.variable
    'x'
    >>> x.coefficients
    {1: <MOnumber 1>}
    >>> x.degree
    1
    """

    def __init__(self, value):
        """ Initiate a string MO

        >>> a = MOstr("x")
        >>> a
        <MOstr x>
        >>> b = MOstr(a)
        >>> b
        <MOstr x>

        >>> a = MOstr("+")
        Traceback (most recent call last):
            ...
        mapytex.calculus.core.MO.exceptions.MOError: An MOstr should be initiate with a alpha string, got +
        >>> MOstr("ui")
        Traceback (most recent call last):
            ...
        mapytex.calculus.core.MO.exceptions.MOError: An MOstr should be initiate with a single caracter string, got ui
        >>> MOstr(2)
        Traceback (most recent call last):
            ...
        mapytex.calculus.core.MO.exceptions.MOError: An MOstr should be initiate with a string - the unknown, got 2

        """

        if isinstance(value, Atom):
            val = value.value
        else:
            val = value

        if not isinstance(val, str):
            raise MOError(
                f"An MOstr should be initiate with a string - the unknown, got {val}"
            )
        if len(val) != 1:
            raise MOError(
                f"An MOstr should be initiate with a single caracter string, got {val}"
            )
        if not val.isalpha():
            raise MOError(f"An MOstr should be initiate with a alpha string, got {val}")

        Atom.__init__(self, val)

        self.is_scalar = False
        self._signature = "monome1"

        self._variable = val

    @property
    def variable(self):
        return self._variable

    @property
    def coefficients(self):
        """ Dictionnary of coefficients

        :example:
        >>> p = MOstr("x")
        >>> p.coefficients
        {1: <MOnumber 1>}
        """

        return {1: MOnumber(1)}

    @property
    def degree(self):
        return 1


# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
