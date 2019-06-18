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
    "Country"
]


from .databaseobject import (
    DatabaseObject
)
from .inputsystem import (
    InputSystem
)


class Country(DatabaseObject):
    _ChildClass = InputSystem

    @property
    def children(self):
        try:
            self._children
        except AttributeError:
            self._children = []

            table = self._html.\
                find(lambda x: x.name == "h2" and x.text.find("Elephant Estimates") > -1).next_sibling  # noqa: E501

            columns = []

            for tr in table.findAll("tr")[1:]:

                for th in tr.findAll("th"):  # let’s hope th comes before td
                    columns.append(th.text.strip())

                values = []
                for td in tr.findAll("td"):
                    text = td.text.strip()
                    if td.has_attr("colspan"):
                        break
                    else:
                        if text[:2] == "+ ":
                            text = text[2:]
                        values.append(text)

                if len(values):
                    if tr.has_attr("data-section"):
                        stratum = {
                            columns[i]: values[i] for i in range(len(values))
                        }
                        stratum["href"] = tr.find("a")["href"]
                        try:
                            self._children[-1]["strati"]
                        except KeyError:
                            self._children[-1]["strati"] = []
                        self._children[-1]["strati"].append(stratum)
                    else:
                        child = self._ChildClass(
                            self._url,
                            {
                                columns[i]: values[i]
                                for i in range(len(values))
                            }
                        )

                    self._children.append(child)

        return self._children
