# -*- coding: utf-8 -*-
# Copyright (C) 2018-2019 Team tiramisu (see AUTHORS for all contributors)
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# ____________________________________________________________


class Cache(object):
    __slots__ = ('_cache',)

    def __init__(self):
        self._cache = {}

    def _setcache(self, path, index, val, time):
        self._cache.setdefault(path, {})[index] = (val, int(time))

    def _getcache(self, path, index):
        values = self._cache.get(path)
        if values is None:
            return
        return values.get(index)

    def _delcache(self, path):
        del self._cache[path]

    def _get_cached(self):
        return self._cache

    def _reset_all_cache(self):
        self._cache.clear()
