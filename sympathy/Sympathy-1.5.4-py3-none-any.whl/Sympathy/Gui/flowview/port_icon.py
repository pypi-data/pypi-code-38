# -*- coding: utf-8 -*-
# This file is part of Sympathy for Data.
# Copyright (c) 2017 Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
import svgutils
import os
from sympathy.types import types
from ..util import icon_path


def icon(datatype, icons):
    root = _Node()
    _tokenize(root, datatype, icons)
    return(_build_icon(root.list()))


_HEIGHT = '16'
_UNKNOWN = icon_path('ports/unknown.svg')
_LAMBDA = icon_path('ports/lambda.svg')
_COMMA = icon_path('ports/comma.svg')
_L_BRK = icon_path('ports/left_bracket.svg')
_R_BRK = icon_path('ports/right_bracket.svg')
_L_PAREN = icon_path('ports/left_parenthesis.svg')
_R_PAREN = icon_path('ports/right_parenthesis.svg')
_LIST = 'list'
_TUPLE = 'tuple'


class _Node(object):
    def __init__(self, data=None):
        super(_Node, self).__init__()
        self._data = data
        self._children = []

    def add_child(self, data):
        node = _Node(data)
        self._children.append(node)
        return node

    def list(self):
        """Post order traversal."""
        l = []
        for child in self._children:
            l.extend(child.list())
        if len(self._children) == 0:
            if self._data is None:
                l.append(_UNKNOWN)
            elif not os.path.isabs(self._data):
                l.append(icon_path(self._data))
            else:
                l.append(self._data)
        elif self._data == _LIST:
            l.insert(0, _L_BRK)
            l.append(_R_BRK)
        elif self._data == _TUPLE:
            l.insert(0, _L_PAREN)
            l.append(_R_PAREN)
        return l


def _build_icon(symbols):
    svg = svgutils.transform.SVGFigure(1, 1)
    offset = 0
    for s in symbols:
        try:
            element = svgutils.transform.fromfile(s)
            height = float(element.get_size()[1])
            if int(height) != int(_HEIGHT):
                scale = float(_HEIGHT) / height
                length = int(_HEIGHT)
            else:
                scale = 1
                length = int(element.get_size()[0])
            root = element.getroot()
            root.moveto(offset, 0, scale)
            svg.append(root)
            offset += length
        except (OSError, IOError):
            continue
    if offset != 0:
        svg.set_size((str(offset), _HEIGHT))
        # The viewbox attribute in the generated SVG's are
        # incorrect. Due to spelling misstake in svgutil-0.2.2 this
        # was never a problem. In later svgutils this spelling have
        # been corrected and thus now give incorrect SVG's.
        #
        # Ugly hack: replace "viewBox" with "ignored_viewbox" fixes
        # the problem for now
        as_str = svg.to_str()
        as_str = as_str.replace(b'ASCII', b'UTF-8')
        as_str = as_str.replace(b'viewBox', b'ignored_viewbox')
        return as_str

    with open(_UNKNOWN, 'rb') as file:
        return file.read()


def _tokenize(node, datatype, icons):
    if isinstance(datatype, types.TypeAlias):
        try:
            node = node.add_child(icons[str(datatype)])
        except KeyError:
            # Datatype is missing
            node = node.add_child(_UNKNOWN)
    elif isinstance(datatype, types.TypeFunction):
        node = node.add_child(_LAMBDA)
    elif isinstance(datatype, types.TypeGeneric):
        node = node.add_child(_UNKNOWN)
    elif isinstance(datatype, types.TypeList):
        node = node.add_child(_LIST)
        for item in datatype.items():
            _tokenize(node, item, icons)
    elif isinstance(datatype, types.TypeTuple):
        node = node.add_child(_TUPLE)
        for i, item in enumerate(datatype):
            if i > 0:
                node.add_child(_COMMA)
            _tokenize(node, item, icons)
    return node
