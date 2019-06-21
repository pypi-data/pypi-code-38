# -*- coding: utf-8 -*-
"default plugin for value: set it in a simple dictionary"
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
from ..util import Cache
from ...setting import undefined
from ...i18n import _
from ...log import log

from copy import deepcopy


class Values(Cache):
    __slots__ = ('_values',
                 '_informations',
                 '__weakref__')

    def __init__(self, storage):
        """init plugin means create values storage
        """
        #(('path1',), (index1,), (value1,), ('owner1'))
        self._values = ([], [], [], [])
        self._informations = {}
        # should init cache too
        super(Values, self).__init__(storage)

    def commit(self):
        pass

    def _setvalue_info(self, nb, idx, value, index, follower_idx=None):
        lst = self._values[nb]
        if index is None or nb == 0:
            # not follower or path
            lst[idx] = value
        else:
            # follower
            if nb == 1 and index in lst[idx]:
                follower_idx = lst[idx].index(index)
            tval = list(lst[idx])
            if follower_idx is None:
                tval.append(value)
            else:
                tval[follower_idx] = value
            lst[idx] = tval
        return follower_idx

    def _add_new_value(self, index, nb, value):
        if index is None or nb == 0:
            # not follower or path
            self._values[nb].append(value)
        else:
            # follower
            self._values[nb].append([value])

    # value
    def setvalue(self,
                 path,
                 value,
                 owner,
                 index,
                 commit):
        """set value for a path
        a specified value must be associated to an owner
        """
        log.debug('setvalue %s %s %s %s %s', path, value, owner, index, id(self))

        #if isinstance(value, list):
        #    value = value
        if path in self._values[0]:
            idx = self._values[0].index(path)
            self._setvalue_info(0, idx, path, index)
            follower_idx = self._setvalue_info(1, idx, index, index)
            self._setvalue_info(2, idx, value, index, follower_idx)
            self._setvalue_info(3, idx, owner, index, follower_idx)
        else:
            self._add_new_value(index, 0, path)
            self._add_new_value(index, 1, index)
            self._add_new_value(index, 2, value)
            self._add_new_value(index, 3, owner)

    def hasvalue(self, path, index=None):
        """if path has a value
        return: boolean
        """
        has_path = path in self._values[0]
        log.debug('hasvalue %s %s %s %s', path, index, has_path, id(self))
        if index is None:
            return has_path
        elif has_path:
            path_idx = self._values[0].index(path)
            indexes = self._values[1][path_idx]
            return index in indexes
        return False

    def reduce_index(self, path, index):
        """
        _values == ((path1, path2), ((idx1_1, idx1_2), None), ((value1_1, value1_2), value2), ((owner1_1, owner1_2), owner2))
        """
        log.debug('reduce_index %s %s %s', path, index, id(self))
        path_idx = self._values[0].index(path)
        # get the "index" position
        subidx = self._values[1][path_idx].index(index)
        # reduce to one the index
        self._values[1][path_idx][subidx] -= 1

    def resetvalue_index(self,
                         path,
                         index,
                         commit):
        log.debug('resetvalue_index %s %s %s', path, index, id(self))
        def _resetvalue(nb):
            del self._values[nb][path_idx]

        def _resetvalue_index(nb):
            del self._values[nb][path_idx][subidx]

        path_idx = self._values[0].index(path)
        indexes = self._values[1][path_idx]
        if index in indexes:
            subidx = indexes.index(index)
            if len(self._values[1][path_idx]) == 1:
                _resetvalue(0)
                _resetvalue(1)
                _resetvalue(2)
                _resetvalue(3)
            else:
                _resetvalue_index(1)
                _resetvalue_index(2)
                _resetvalue_index(3)

    def resetvalue(self,
                   path,
                   commit):
        """remove value means delete value in storage
        """
        log.debug('resetvalue %s %s', path, id(self))
        def _resetvalue(nb):
            self._values[nb].pop(idx)
        if path in self._values[0]:
            idx = self._values[0].index(path)
            _resetvalue(0)
            _resetvalue(1)
            _resetvalue(2)
            _resetvalue(3)

    # owner
    def setowner(self,
                 path,
                 owner,
                 index=None):
        """change owner for a path
        """
        idx = self._values[0].index(path)
        if index is None:
            follower_idx = None
        else:
            follower_idx = self._values[1][idx].index(index)
        self._setvalue_info(3, idx, owner, index, follower_idx)

    def get_max_length(self,
                       path):
        if path in self._values[0]:
            idx = self._values[0].index(path)
        else:
            return 0
        return max(self._values[1][idx]) + 1

    def getowner(self,
                 path,
                 default,
                 index=None,
                 with_value=False):
        """get owner for a path
        return: owner object
        """
        owner, value = self._getvalue(path,
                                      index,
                                      with_value)
        if owner is undefined:
            owner = default
        log.debug('getvalue %s %s %s %s %s', path, index, value, owner, id(self))
        if with_value:
            return owner, value
        else:
            return owner

    def _getvalue(self,
                  path,
                  index,
                  with_value):
        """
        _values == ((path1, path2), ((idx1_1, idx1_2), None), ((value1_1, value1_2), value2), ((owner1_1, owner1_2), owner2))
        """
        value = undefined
        if path in self._values[0]:
            path_idx = self._values[0].index(path)
            indexes = self._values[1][path_idx]
            if indexes is None:
                if index is not None:  # pragma: no cover
                    raise ValueError('index is forbidden for {}'.format(path))
                owner = self._values[3][path_idx]
                if with_value:
                    value = self._values[2][path_idx]
            else:
                if index is None:  # pragma: no cover
                    raise ValueError('index is mandatory for {}'.format(path))
                if index in indexes:
                    subidx = indexes.index(index)
                    owner = self._values[3][path_idx][subidx]
                    if with_value:
                        value = self._values[2][path_idx][subidx]
                else:
                    owner = undefined
        else:
            owner = undefined
        if isinstance(value, tuple):
            value = list(value)
        return owner, value

    def set_information(self, path, key, value):
        """updates the information's attribute
        (which is a dictionary)

        :param key: information's key (ex: "help", "doc"
        :param value: information's value (ex: "the help string")
        """
        self._informations.setdefault(path, {})
        self._informations[path][key] = value

    def get_information(self, path, key, default):
        """retrieves one information's item

        :param key: the item string (ex: "help")
        """
        value = self._informations.get(path, {}).get(key, default)
        if value is undefined:
            raise ValueError(_("information's item"
                               " not found: {0}").format(key))
        return value

    def del_information(self, path, key, raises):
        if path in self._informations and key in self._informations[path]:
            del self._informations[path][key]
        else:
            if raises:
                raise ValueError(_("information's item not found {0}").format(key))

    def list_information(self, path):
        if path in self._informations:
            return self._informations[path].keys()
        else:
            return []

    def del_informations(self):
        self._informations = {}

    def exportation(self):
        return deepcopy(self._values)

    def importation(self, export):
        self._values = deepcopy(export)


def delete_session(session_id):
    raise ValueError(_('cannot delete none persistent session'))
