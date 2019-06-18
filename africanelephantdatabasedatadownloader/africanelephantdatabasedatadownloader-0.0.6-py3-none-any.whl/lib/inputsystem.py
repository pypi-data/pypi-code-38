#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#   Copyright (C) 2019 Christoph Fink, University of Helsinki
#
#   This program is free software; you can redistribute it and/or
#   modify it under the terms of the GNU General Public License
#   as published by the Free Software Foundation; either version 3
#   of the License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, see <http://www.gnu.org/licenses/>.

""" A base class for self-aware database objects """

__all__ = [
    "InputSystem"
]


import urllib.parse

from .databaseobject import (
    DatabaseObject
)
from .dictlike import (
    DictLike
)
from .stratum import (
    Stratum
)


class InputSystem(DatabaseObject, DictLike):
    _ChildClass = Stratum

    def __init__(self, url=None, data={}, *args, **kwargs):
        super().__init__(url, *args, **kwargs)
        self.data = data

    @property
    def name(self):
        try:
            self._name
        except AttributeError:
            try:
                self._name = self.data["Input Zone"]
            except KeyError:
                self._name = None
        return self._name

    @property
    def children(self):
        try:
            self._children
        except AttributeError:
            self._children = [
                self._ChildClass(
                    urllib.parse.urljoin(
                        self._url,
                        s["href"]
                    ),
                    s
                )
                for s in self.data["strati"] if "strati" in self.data
            ]
        return self._children
