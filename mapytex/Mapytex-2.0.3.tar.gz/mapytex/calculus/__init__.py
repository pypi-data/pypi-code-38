#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 lafrite <lafrite@Poivre>
#
# Distributed under terms of the MIT license.

"""
Make calculus as a student
==========================

Expression is the classe wich handle all calculus. It can randomly generate or import calculus, simplify them and explain them as a student would do.

>>> from mapytex.calculus import Expression
>>> e = Expression.from_str("2x + 6 - 3x")
>>> print(e)
2x + 6 - 3x
>>> f = e.simplify()
>>> print(f)
- x + 6
>>> for s in f.explain():
...    print(s)
2x + 6 - 3x
2x - 3x + 6
(2 - 3) * x + 6
- x + 6


"""

from .API import Expression

__all__ = [Expression]


# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
