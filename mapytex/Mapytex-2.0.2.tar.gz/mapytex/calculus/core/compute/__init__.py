#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 lafrite <lafrite@Poivre>
#
# Distributed under terms of the MIT license.

"""
Computing with MO
"""

from .exceptions import ComputeError
from .add import add
from .divide import divide
from .minus import minus
from .multiply import multiply
from .power import power

from ..MO import MOnumber, MOstr
from ..MO.fraction import MOFraction
from ..MO.monomial import MOstrPower, MOMonomial
from ..MO.polynomial import MOpolynomial

from itertools import product
from tabulate import tabulate

MOS = [MOnumber, MOstr, MOFraction, MOstrPower, MOMonomial, MOpolynomial]

OPERATIONS = {"+": add, "-": minus, "*": multiply, "/": divide, "^": power}


def compute(node, left_v, right_v):
    """ 
    Computing a node 

    :example:

    >>> from ..MO import MOnumber
    >>> compute("+", MOnumber(1), MOnumber(2))
    <MOnumber 3>
    >>> compute("-", None, MOnumber(2))
    <MOnumber - 2>
    >>> compute("*", MOnumber(1), MOnumber(2))
    <MOnumber 2>
    >>> compute("~", MOnumber(1), MOnumber(2))
    Traceback (most recent call last):
        ...
    mapytex.calculus.core.compute.exceptions.ComputeError: Unknown operation (~) in compute
    """
    try:
        operation = OPERATIONS[node]
    except KeyError:
        raise ComputeError(f"Unknown operation ({node}) in compute")

    return operation(left_v, right_v)


def compute_capacities(node):
    """ Test an operation through all MOs 

    :param operation: string which represent an (mo, mo) -> mo
    :returns: { (motype, motype): True/False } when it's implemented

    :example:
    >>> compute_capacities("+")
    [['+', 'MOnumber', 'MOstr', 'MOFraction', 'MOstrPower', 'MOMonomial', 'MOpolynomial'], ['MOnumber', True, False, True, False, False, True], ['MOstr', False, True, False, False, True, True], ['MOFraction', True, False, True, False, False, True], ['MOstrPower', False, False, False, True, True, True], ['MOMonomial', False, True, False, True, True, True], ['MOpolynomial', True, True, True, True, True, True]]

    """
    op = OPERATIONS[node]
    lines = [[node] + [mo.__name__ for mo in MOS]]
    for left_mo in MOS:
        lines.append([left_mo.__name__] + [(left_mo, i) in op.funcs for i in MOS])
    return lines


def describe_compute():
    """ Explain which operation are handle by compue """

    ans = "Implemented compute operations among MOs"
    for op in OPERATIONS:
        ans += "\n"
        ans += tabulate(compute_capacities(op), tablefmt="grid")
    return ans


# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
