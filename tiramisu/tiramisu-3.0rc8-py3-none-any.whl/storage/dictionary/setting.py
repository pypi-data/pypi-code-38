# -*- coding: utf-8 -*-
"default plugin for setting: set it in a simple dictionary"
# Copyright (C) 2013-2019 Team tiramisu (see AUTHORS for all contributors)
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
from copy import copy
from ..util import Cache
from ...log import log


class Properties(Cache):
    __slots__ = ('_properties',)

    def __init__(self, storage):
        # properties attribute: the name of a property enables this property
        # key is None for global properties
        self._properties = {}
        # permissive properties
        super(Properties, self).__init__(storage)

    # properties
    def setproperties(self, path, properties):
        log.debug('setproperties %s %s', path, properties)
        self._properties[path] = properties

    def getproperties(self, path, default_properties):
        ret = self._properties.get(path, frozenset(default_properties))
        log.debug('getproperties %s %s', path, ret)
        return ret

    def delproperties(self, path):
        log.debug('delproperties %s', path)
        if path in self._properties:
            del(self._properties[path])

    def exportation(self):
        """return all modified settings in a dictionary
        example: {'path1': set(['prop1', 'prop2'])}
        """
        return copy(self._properties)

    def importation(self, properties):
        self._properties = properties


class Permissives(Cache):
    __slots__ = ('_permissives',)

    def __init__(self, storage):
        # permissive properties
        self._permissives = {}
        super(Permissives, self).__init__(storage)

    def setpermissives(self, path, permissives):
        log.debug('setpermissives %s %s', path, permissives)
        if not permissives:
            if path in self._permissives:
                del self._permissives[path]
        else:
            self._permissives[path] = permissives

    def getpermissives(self, path=None):
        ret = self._permissives.get(path, frozenset())
        log.debug('getpermissives %s %s', path, ret)
        return ret

    def exportation(self):
        """return all modified permissives in a dictionary
        example: {'path1': set(['perm1', 'perm2'])}
        """
        return copy(self._permissives)

    def importation(self, permissives):
        self._permissives = permissives

    def delpermissive(self, path):
        log.debug('delpermissive %s', path)
        if path in self._permissives:
            del(self._permissives[path])
