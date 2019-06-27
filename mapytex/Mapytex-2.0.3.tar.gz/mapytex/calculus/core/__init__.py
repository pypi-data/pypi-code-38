#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 lafrite <lafrite@Poivre>
#
# Distributed under terms of the MIT license.

r"""
Abstracts tools for calculs manipulations

:example:

>>> t = Tree.from_str("2+3*4")
>>> print(t)
+
 > 2
 > *
 | > 3
 | > 4
>>> print(t.apply_on_last_level(compute))
+
 > 2
 > 12
>>> tree2txt(t)
'2 + 3 * 4'
>>> tree2tex(t)
'2 + 3 \\times 4'

>>> t = Tree.from_str("2+3/4")
>>> print(t)
+
 > 2
 > /
 | > 3
 | > 4
>>> print(t.apply_on_last_level(compute))
+
 > 2
 > /
 | > 3
 | > 4
>>> tt = t.apply_on_last_level(typing)
>>> print(tt.apply_on_last_level(compute))
+
 > 2 / 1
 > 3 / 4
>>> type(t.right_value)
<class 'mapytex.calculus.core.tree.Tree'>
>>> type(tt.right_value)
<class 'mapytex.calculus.core.MO.fraction.MOFraction'>
>>> tt.right_value
<MOFraction 3 / 4>

>>> t = Tree.from_str("2+3x")
>>> print(t)
+
 > 2
 > *
 | > 3
 | > x

"""

from .tree import Tree, AssocialTree
from .compute import compute
from .typing import typing, TypingError
from .renders import tree2txt, tree2tex


# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
