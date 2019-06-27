#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 lafrite <lafrite@Poivre>
#
# Distributed under terms of the MIT license.

"""
Typing trees with a divide root
"""

from multipledispatch import Dispatcher
from ..MO import MO, MOnumber
from ..MO.fraction import MOFraction

divide_doc = """ Typing trees a divide root

:param left: left MO
:param right: right MO
:returns: MO

"""

divide = Dispatcher("divide", doc=divide_doc)


@divide.register(MOnumber, MOnumber)
def monumber_monumber(left, right):
    """ A divide tree with 2 MOnumbers is a MOFraction

    >>> a = MOnumber(4)
    >>> b = MOnumber(6)
    >>> monumber_monumber(a, b)
    <MOFraction 4 / 6>

    """
    return MOFraction(left, right)


# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
