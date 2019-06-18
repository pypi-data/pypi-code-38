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
    "DatabaseObject"
]


import bs4
import requests
import urllib.parse


class DatabaseObject(object):
    """ Base class for all object types found in the
        African Elephant Database (dbRoot, year, continent,
        region, country, inputSystem, stratum) """

    def __init__(self, url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if url is not None:
            if url[-1] == "/":
                url = url[:-1]
            self._url = url

    def __iter__(self):
        yield from self.children

    @property
    def name(self):
        try:
            self._name
        except AttributeError:
            self._name = self._url[self._url.rfind("/")+1:].replace("_", " ")
        return self._name

    @property
    def _content(self):
        try:
            self.__content
        except AttributeError:
            self.__content = requests.get(
                self._url
            ).text
        return self.__content

    @property
    def _html(self):
        try:
            self.__html
        except AttributeError:
            self.__html = bs4.BeautifulSoup(self._content, "html.parser")
        return self.__html

    @property
    def children(self):
        try:
            self._children
        except AttributeError:
            self._children = [
                self._ChildClass(
                    urllib.parse.urljoin(
                        self._url,
                        a["href"]
                    )
                )
                for a in self._html.select(
                    "#tab-section-data-quality-page-0 table td:not(.numeric) a"
                )
            ]
        return self._children
