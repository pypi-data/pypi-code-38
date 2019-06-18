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
    "DatabaseRoot"
]


from .year import (
    Year
)
from .databaseobject import (
    DatabaseObject
)


class DatabaseRoot(DatabaseObject):
    _url = "http://africanelephantdatabase.org/report/"
    _ChildClass = Year

    @property
    def children(self):
        try:
            self._children
        except AttributeError:
            # hard-coded is fine for now :D
            self._children = [
                self._ChildClass(
                    "http://africanelephantdatabase.org/report/{year:d}".format(  # noqa: E501
                        year=year
                    )
                )
                for year in [2016]  # [1995, 1998, 2002, 2007, 2013, 2016]
            ]
        return self._children
