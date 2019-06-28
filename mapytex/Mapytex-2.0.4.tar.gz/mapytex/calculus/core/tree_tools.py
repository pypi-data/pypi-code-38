#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 lafrite <lafrite@Poivre>
#
# Distributed under terms of the MIT license.

"""
Functions to manipulate trees
"""

__all__ = []

# Functions on leaf


# Functions on (op, left, right)


def to_nested_parenthesis(op, left, right):
    """ Get nested form for arguments

    :exemple:

    >>> to_nested_parenthesis('+', 3, 4)
    ('+', (3, 4))
    """
    return (op, (left, right))


def infix_str_concatenate(op, left, right):
    """ Concatenate arguments placing op on the middle.

    :example:

    >>> infix_str_concatenate('+', 1, 2)
    '1 + 2'
    """
    return f"{left} {op} {right}"


def postfix_concatenate(op, left, right):
    """ Concatenate arguments placing op on the middle.

    :example:

    >>> postfix_concatenate('+', 1, 2)
    [1, 2, '+']
    >>> p = postfix_concatenate('+', 1, 2)
    >>> postfix_concatenate('*', p, 3)
    [1, 2, '+', 3, '*']
    >>> postfix_concatenate('*', 3, p)
    [3, 1, 2, '+', '*']
    """
    if isinstance(left, list):
        left_tokens = left
    else:
        left_tokens = [left]
    if isinstance(right, list):
        right_tokens = right
    else:
        right_tokens = [right]

    return left_tokens + right_tokens + [op]


def show_tree(op, left, right, sep="|", node_caracter=">"):
    """ Shape argument to make nice Tree display

    :example:

    >>> print(show_tree("+", 1, 2))
    +
     > 1
     > 2
    >>> t1 = show_tree("*", 1, 2)
    >>> print(show_tree("+", t1, 3))
    +
     > *
     | > 1
     | > 2
     > 3

    """
    node_suffix = f"\n {node_caracter} "
    leaf_suffix = f"\n {sep}"
    left_slided = leaf_suffix.join(str(left).splitlines())
    right_slided = leaf_suffix.join(str(right).splitlines())
    return node_suffix.join([op, left_slided, right_slided])


# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
