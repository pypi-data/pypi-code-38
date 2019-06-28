#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 lafrite <lafrite@Poivre>
#
# Distributed under terms of the MIT license.

from mapytex.calculus.core.operator import OPERATORS

__all__ = ["tree2tex"]


def plus2tex(left, right):
    r""" + rendering

    >>> from ..MO import MO
    >>> plus2tex(MO.factory(2), MO.factory(3))
    '2 + 3'
    >>> from ..tree import Tree
    >>> t = Tree.from_str("1+2")
    >>> plus2tex(t, MO.factory(3))
    '1 + 2 + 3'
    >>> plus2tex(t, MO.factory(-3))
    '1 + 2 - 3'
    >>> plus2tex(MO.factory(-3), t)
    '- 3 + 1 + 2'
    >>> t = Tree.from_str("-2*3")
    >>> plus2tex(MO.factory(3), t)
    '3 - 2 \\times 3'
    """
    display_plus = True
    try:
        left.node
    except AttributeError:
        left_ = left.__tex__
    else:
        left_ = tree2tex(left)

    try:
        right.node
    except AttributeError:
        right_ = right.__tex__
    else:
        right_ = tree2tex(right)
    finally:
        if right_.startswith("-"):
            display_plus = False

    if display_plus:
        return f"{left_} + {right_}"

    return f"{left_} {right_}"


def minus2tex(left, right):
    r""" - rendering

    >>> from ..MO import MO
    >>> minus2tex(None, MO.factory(3))
    '- 3'
    >>> from ..tree import Tree
    >>> t = Tree.from_str("1+2")
    >>> minus2tex(None, t)
    '- (1 + 2)'
    """
    try:
        right_need_parenthesis = False
        if OPERATORS[right.node]["precedence"] < OPERATORS["-"]["precedence"]:
            right_need_parenthesis = True
    except AttributeError:
        right_ = right.__tex__
    else:
        if right_need_parenthesis:
            right_ = f"({tree2tex(right)})"
        else:
            right_ = tree2tex(right)

    return f"- {right_}"


def mul2tex(left, right):
    r""" * rendering

    >>> from ..MO import MO
    >>> mul2tex(MO.factory(2), MO.factory(3))
    '2 \\times 3'
    >>> from ..tree import Tree
    >>> t = Tree.from_str("1*2")
    >>> mul2tex(t, MO.factory(3))
    '1 \\times 2 \\times 3'
    >>> t = Tree.from_str("1+2")
    >>> mul2tex(t, MO.factory(3))
    '(1 + 2) \\times 3'
    >>> mul2tex(MO.factory(3), t)
    '3(1 + 2)'
    >>> a = MO.factory('x')
    >>> mul2tex(MO.factory(3), a)
    '3x'
    >>> mul2tex(a, a)
    'x \\times x'
    """
    left_ = render_with_parenthesis(left, "*")
    right_ = render_with_parenthesis(right, "*")

    display_time = True
    if (right_[0].isalpha() and (left_.isnumeric() or left_.isdecimal())) or right_[
        0
    ] == "(":
        display_time = False

    if display_time:
        return f"{left_} \\times {right_}"
    return f"{left_}{right_}"


def div2tex(left, right):
    r""" / rendering

    >>> from ..MO import MO
    >>> div2tex(MO.factory(2), MO.factory(3))
    '\\frac{2}{3}'
    >>> from ..tree import Tree
    >>> t = Tree.from_str("1/2")
    >>> div2tex(t, MO.factory(3))
    '\\frac{\\frac{1}{2}}{3}'
    >>> t = Tree.from_str("1+2")
    >>> div2tex(t, MO.factory(3))
    '\\frac{1 + 2}{3}'
    >>> t = Tree.from_str("1*2")
    >>> div2tex(MO.factory(3), t)
    '\\frac{3}{1 \\times 2}'
    """
    try:
        left_ = tree2tex(left)
    except AttributeError:
        left_ = left.__tex__
    try:
        right_ = tree2tex(right)
    except AttributeError:
        right_ = right.__tex__

    return "\\frac{" + left_ + "}{" + right_ + "}"


def pow2tex(left, right):
    r""" ^ rendering

    >>> from ..MO import MO
    >>> pow2tex(MO.factory(2), MO.factory(3))
    '2^{3}'
    >>> from ..tree import Tree
    >>> t = Tree.from_str("1^2")
    >>> pow2tex(t, MO.factory(3))
    '1^{2}^{3}'
    >>> t = Tree.from_str("1^2")
    >>> pow2tex(MO.factory(3), t)
    '3^{1^{2}}'
    >>> t = Tree.from_str("1+2")
    >>> pow2tex(t, MO.factory(3))
    '(1 + 2)^{3}'
    >>> t = Tree.from_str("1*2")
    >>> pow2tex(MO.factory(3), t)
    '3^{1 \\times 2}'
    """
    try:
        left_need_parenthesis = False
        if OPERATORS[left.node]["precedence"] < OPERATORS["^"]["precedence"]:
            left_need_parenthesis = True
    except AttributeError:
        left_ = left.__tex__
    else:
        if left_need_parenthesis:
            left_ = f"({tree2tex(left)})"
        else:
            left_ = tree2tex(left)

    try:
        right.node
    except AttributeError:
        right_ = right.__tex__
    else:
        right_ = tree2tex(right)

    return f"{left_}^{{{right_}}}"


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
        subtree_ = tree2tex(subtree)

    if subtree_need_parenthesis:
        return f"({subtree_})"
    return subtree_


OPERATOR2TEX = {"+": plus2tex, "-": minus2tex, "*": mul2tex, "/": div2tex, "^": pow2tex}


def tree2tex(tree):
    r""" Convert a tree into its tex version

    It calls __tex__ to render MOs.

    :param tree: tree to render

    :example:

    >>> from ..tree import Tree
    >>> t = Tree.from_str("2+3*4")
    >>> tree2tex(t)
    '2 + 3 \\times 4'
    """
    return OPERATOR2TEX[tree.node](tree.left_value, tree.right_value)


# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
