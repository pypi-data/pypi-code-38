#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 lafrite <lafrite@Poivre>
#
# Distributed under terms of the MIT license.

__all__ = ["OperatorError", "OPERATORS", "is_operator"]


class OperatorError(Exception):
    pass


OPERATORS = {
    "+": {"repr": "+", "arity": 2, "precedence": 0},
    "-": {"repr": "-", "arity": 1, "precedence": 1},
    "*": {"repr": "*", "arity": 2, "precedence": 2},
    "/": {"repr": "/", "arity": 2, "precedence": 3},
    "^": {"repr": "^", "arity": 2, "precedence": 4},
}


def is_operator(string):
    """ Return whether a string is an operator or not

    :param string: string to test
    :returns: boolean

    :example:

    >>> is_operator("+")
    True
    >>> is_operator("i")
    False

    """
    return string in OPERATORS.keys()


# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
