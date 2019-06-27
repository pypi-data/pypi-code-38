#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 lafrite <lafrite@Poivre>
#
# Distributed under terms of the MIT license.

from ..operator import OPERATORS

__all__ = ["tree2txt"]


def plus2txt(left, right):
    """ + rendering

    >>> from ..MO import MO
    >>> plus2txt(MO.factory(2), MO.factory(3))
    '2 + 3'
    >>> from ..tree import Tree
    >>> t = Tree.from_str("1+2")
    >>> plus2txt(t, MO.factory(3))
    '1 + 2 + 3'
    >>> plus2txt(t, MO.factory(-3))
    '1 + 2 - 3'
    >>> plus2txt(MO.factory(-3), t)
    '- 3 + 1 + 2'
    >>> t = Tree.from_str("-2*3")
    >>> plus2txt(MO.factory(3), t)
    '3 - 2 * 3'
    """

    left_ = render_with_parenthesis(left, "+")
    right_ = render_with_parenthesis(right, "+")

    display_plus = True
    if right_.startswith("-"):
        display_plus = False

    if display_plus:
        return f"{left_} + {right_}"

    return f"{left_} {right_}"


def minus2txt(left, right):
    """ - rendering

    >>> from ..MO import MO
    >>> minus2txt(None, MO.factory(3))
    '- 3'
    >>> from ..tree import Tree
    >>> t = Tree.from_str("1+2")
    >>> minus2txt(None, t)
    '- (1 + 2)'
    """
    try:
        right_need_parenthesis = False
        if OPERATORS[right.node]["precedence"] < OPERATORS["-"]["precedence"]:
            right_need_parenthesis = True
    except AttributeError:
        right_ = right.__txt__
    else:
        if right_need_parenthesis:
            right_ = f"({tree2txt(right)})"
        else:
            right_ = tree2txt(right)

    return f"- {right_}"


def mul2txt(left, right):
    """ * rendering

    >>> from ..MO import MO
    >>> mul2txt(MO.factory(2), MO.factory(3))
    '2 * 3'
    >>> from ..tree import Tree
    >>> t = Tree.from_str("1*2")
    >>> mul2txt(t, MO.factory(3))
    '1 * 2 * 3'
    >>> t = Tree.from_str("1+2")
    >>> mul2txt(t, MO.factory(3))
    '(1 + 2) * 3'
    >>> mul2txt(MO.factory(3), t)
    '3(1 + 2)'
    >>> a = MO.factory('x')
    >>> mul2txt(MO.factory(3), a)
    '3x'
    >>> mul2txt(MO.factory(-3), a)
    '- 3x'
    >>> mul2txt(a, a)
    'x * x'
    """
    display_time = True

    left_ = render_with_parenthesis(left, "*")
    right_ = render_with_parenthesis(right, "*")

    if right_[0].isalpha():
        # TODO: C'est bien beurk en dessous... |ven. déc. 21 12:03:07 CET 2018
        if type(left).__name__ == "MOnumber":
            display_time = False
    elif right_[0] == "(":
        display_time = False

    if display_time:
        return f"{left_} * {right_}"
    else:
        return f"{left_}{right_}"


def div2txt(left, right):
    """ / rendering

    >>> from ..MO import MO
    >>> div2txt(MO.factory(2), MO.factory(3))
    '2 / 3'
    >>> from ..tree import Tree
    >>> t = Tree.from_str("1/2")
    >>> div2txt(t, MO.factory(3))
    '1 / 2 / 3'
    >>> t = Tree.from_str("1+2")
    >>> div2txt(t, MO.factory(3))
    '(1 + 2) / 3'
    >>> t = Tree.from_str("1*2")
    >>> div2txt(MO.factory(3), t)
    '3 / (1 * 2)'
    """
    try:
        left_need_parenthesis = False
        if OPERATORS[left.node]["precedence"] < OPERATORS["/"]["precedence"]:
            left_need_parenthesis = True
    except AttributeError:
        left_ = left.__txt__
    else:
        if left_need_parenthesis:
            left_ = f"({tree2txt(left)})"
        else:
            left_ = tree2txt(left)
    try:
        right_need_parenthesis = False
        if OPERATORS[right.node]["precedence"] < OPERATORS["/"]["precedence"]:
            right_need_parenthesis = True
    except AttributeError:
        right_ = right.__txt__
    else:
        if right_need_parenthesis:
            right_ = f"({tree2txt(right)})"
        else:
            right_ = tree2txt(right)

    return f"{left_} / {right_}"


def pow2txt(left, right):
    """ ^ rendering

    >>> from ..MO import MO
    >>> pow2txt(MO.factory(2), MO.factory(3))
    '2^3'
    >>> from ..tree import Tree
    >>> t = Tree.from_str("1^2")
    >>> pow2txt(t, MO.factory(3))
    '1^2^3'
    >>> t = Tree.from_str("1+2")
    >>> pow2txt(t, MO.factory(3))
    '(1 + 2)^3'
    >>> t = Tree.from_str("1*2")
    >>> pow2txt(MO.factory(3), t)
    '3^(1 * 2)'
    """
    left_ = render_with_parenthesis(left, "^")

    try:
        right_need_parenthesis = False
        if OPERATORS[right.node]["precedence"] < OPERATORS["^"]["precedence"]:
            right_need_parenthesis = True
    except AttributeError:
        right_ = right.__txt__
    else:
        if right_need_parenthesis:
            right_ = f"({tree2txt(right)})"
        else:
            right_ = tree2txt(right)

    return f"{left_}^{right_}"


def render_with_parenthesis(subtree, operator):
    subtree_need_parenthesis = False
    try:
        subtree.node
    except AttributeError:
        try:
            if (
                OPERATORS[subtree.MAINOP]["precedence"]
                < OPERATORS[operator]["precedence"]
            ):
                subtree_need_parenthesis = True
        except (AttributeError, KeyError):
            pass
        subtree_ = subtree.__txt__
    else:
        if OPERATORS[subtree.node]["precedence"] < OPERATORS[operator]["precedence"]:
            subtree_need_parenthesis = True
        subtree_ = tree2txt(subtree)

    if subtree_need_parenthesis:
        return f"({subtree_})"
    return subtree_


OPERATOR2TXT = {"+": plus2txt, "-": minus2txt, "*": mul2txt, "/": div2txt, "^": pow2txt}


def tree2txt(tree):
    """ Convert a tree into its txt version

    It calls __txt__ to render MOs.

    :param tree: tree to render

    :example:

    >>> from ..tree import Tree
    >>> t = Tree.from_str("2+3*4")
    >>> tree2txt(t)
    '2 + 3 * 4'
    """
    from ..tree import Tree

    if not isinstance(tree, Tree):
        raise ValueError(f"Can only render a Tree (got {type(tree).__name__}: {tree})")
    return OPERATOR2TXT[tree.node](tree.left_value, tree.right_value)


# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
