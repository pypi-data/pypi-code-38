#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 lafrite <lafrite@Poivre>
#
# Distributed under terms of the MIT license.

"""
Generate and compute like a student!

:example:

>>> e = Expression.from_str("2+3*4")
>>> e_simplified = e.simplify()
>>> print(e_simplified)
14
>>> for s in e_simplified.explain():
...    print(s)
2 + 3 * 4
2 + 12
14


>>> e = Expression.from_str("2+3/2")
>>> e_simplified = e.simplify()
>>> print(e_simplified)
7 / 2
>>> for s in e_simplified.explain():
...    print(s)
2 + 3 / 2
2 / 1 + 3 / 2
(2 * 2) / (1 * 2) + 3 / 2
4 / 2 + 3 / 2
(4 + 3) / 2
7 / 2

>>> e = Expression.from_str("(2+3)/2 + 1")
>>> e_simplified = e.simplify()
>>> print(e_simplified)
7 / 2
>>> for s in e_simplified.explain():
...    print(s)
(2 + 3) / 2 + 1
5 / 2 + 1
5 / 2 + 1 / 1
5 / 2 + (1 * 2) / (1 * 2)
5 / 2 + 2 / 2
(5 + 2) / 2
7 / 2

>>> e = Expression.from_str("(2/3)^4")
>>> e_simplified = e.simplify()
>>> print(e_simplified)
16 / 81
>>> for s in e_simplified.explain():
...    print(s)
(2 / 3)^4
2^4 / 3^4
16 / 81

>>> e = Expression.from_str("x^2*x*x^4")
>>> e_simplified = e.simplify()
>>> e_simplified
<Polynomial x^7>
>>> for s in e_simplified.explain():
...    print(s)
x^2 * x * x^4
x^3 * x^4
x^(3 + 4)
x^7

>>> e = Expression.from_str("2x+2+3x")
>>> e_simplified = e.simplify()
>>> e_simplified
<Linear 5x + 2>
>>> for s in e_simplified.explain():
...    print(s)
2x + 2 + 3x
2x + 3x + 2
(2 + 3) * x + 2
5x + 2

>>> e = Expression.from_str("1+2x^2+3x+4+5x")
>>> e_simplified = e.simplify()
>>> e_simplified
<Quadratic 5 + 2x^2 + 8x>
>>> for s in e_simplified.explain():
...    print(s)
1 + 2x^2 + 3x + 4 + 5x
1 + 2x^2 + 3x + 4 + 5x
1 + 4 + 2x^2 + 3x + 5x
5 + 2x^2 + (3 + 5) * x
5 + 2x^2 + 8x

>>> e = Expression.from_str("(2x+3)^2")
>>> e_simplified = e.simplify()
>>> e_simplified
<Quadratic 12x + 4x^2 + 9>
>>> for s in e_simplified.explain():
...    print(s)
(2x + 3)^2
(2x + 3)(2x + 3)
2x * 2x + 2x * 3 + 3 * 2x + 3 * 3
2 * 2 * x^(1 + 1) + 3 * 2 * x + 3 * 2 * x + 9
6x + 6x + 4x^2 + 9
(6 + 6) * x + 4x^2 + 9
12x + 4x^2 + 9

"""

from .expression import Expression

if __name__ == "__main__":
    e = Expression.from_str("1+2/3/4/5")
    et = e._typing()
    print("typing")
    print(e._tree)
    e = et._order()
    print("order")
    print(e._tree)
    e = e._optimize()
    print("then optimize")
    print(e._tree)
    e = et._optimize()
    print("optimize without order")
    print(e._tree)

# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
