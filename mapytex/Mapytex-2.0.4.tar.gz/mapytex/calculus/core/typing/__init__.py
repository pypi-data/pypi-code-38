#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 lafrite <lafrite@Poivre>
#
# Distributed under terms of the MIT license.

"""
Typing with MO
"""

from .exceptions import TypingError
from .add import add

# from .minus import minus
from .multiply import multiply
from .divide import divide
from .power import power

from ..MO import MOnumber, MOstr
from ..MO.fraction import MOFraction
from ..MO.monomial import MOstrPower, MOMonomial
from ..MO.polynomial import MOpolynomial

from itertools import product
from tabulate import tabulate

MOS = [MOnumber, MOstr, MOFraction, MOstrPower, MOMonomial, MOpolynomial]

OPERATIONS = {
    "+": add,
    # "-": minus,
    "*": multiply,
    "/": divide,
    "^": power,
}


def typing(node, left_v, right_v, raiseTypingError=True):
    """
    Typing a try base on his root node

    """
    try:
        operation = OPERATIONS[node]
    except KeyError:
        raise NotImplementedError(f"Unknown operation ({node}) in typing")
    return operation(left_v, right_v)


def typing_capacities(node):
    """ Test an operation through all MOs

    :param operation: string which represent an (mo, mo) -> mo
    :returns: { (motype, motype): True/False } when it's implemented

    :example:
    >>> typing_capacities("*")
    [['*', 'MOnumber', 'MOstr', 'MOFraction', 'MOstrPower', 'MOMonomial', 'MOpolynomial'], ['MOnumber', False, True, False, True, False, False], ['MOstr', True, False, True, False, False, False], ['MOFraction', False, True, False, True, False, False], ['MOstrPower', True, False, True, False, False, False], ['MOMonomial', False, False, False, False, False, False], ['MOpolynomial', False, False, False, False, False, False]]

    """
    op = OPERATIONS[node]
    lines = [[node] + [mo.__name__ for mo in MOS]]
    for left_mo in MOS:
        lines.append([left_mo.__name__] + [(left_mo, i) in op.funcs for i in MOS])
    return lines


def describe_typing():
    """ Explain which operations are handle by typing """

    ans = "Implemented typing operations among MOs\n"
    for op in OPERATIONS:
        ans += "\n"
        ans += tabulate(typing_capacities(op), tablefmt="grid")

    return ans


# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
