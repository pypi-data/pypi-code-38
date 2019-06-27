#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 lafrite <lafrite@Poivre>
#
# Distributed under terms of the MIT license.

"""
Typing Power with MO
"""

from multipledispatch import Dispatcher
from ..tree import Tree
from ..MO import MO, MOnumber, MOstr
from ..MO.monomial import MOstrPower

power_doc = """ Typing Power of MOs

:param left: left MO
:param right: right MO
:returns: MO

"""

power = Dispatcher("power", doc=power_doc)


@power.register(MOstr, MOnumber)
def mostr_monumber(left, right):
    """ Create MOstrPower over powered MOstr

    >>> a = MOstr("x")
    >>> b = MOnumber(6)
    >>> power(a, b)
    <MOstrPower x^6>

    """
    return MOstrPower(left, right)


# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
