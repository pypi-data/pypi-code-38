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


class Values(Cache):
    __slots__ = ('_values',
                 '_informations',
                 '__weakref__')

    def __init__(self, storage):
        """init plugin means create values storage
        """
        #(('path1',), (index1,), (value1,), ('owner1'))
        self._values = (tuple(), tuple(), tuple(), tuple())
        self._informations = {}
        # should init cache too
        super(Values, self).__init__(storage)

    def commit(self):
        pass

    def _setvalue_info(self, nb, idx, value, values, index, vidx):
        lst = list(self._values[nb])
        if idx is None:
            if index is None or nb == 0:
                lst.append(value)
            else:
                lst.append((value,))
        else:
            if index is None or nb == 0:
                lst[idx] = value
            else:
                if nb == 1:
                    if index in lst[idx]:
                        vidx = lst[idx].index(index)
                    else:
                        vidx = None
                if vidx is None:
                    tval = list(lst[idx])
                    tval.append(value)
                    lst[idx] = tuple(tval)
                elif nb != 1:
                    tval = list(lst[idx])
                    tval[vidx] = value
                    lst[idx] = tuple(tval)
                lst[idx] = tuple(lst[idx])
        values.append(tuple(lst))
        return vidx

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
        values = []
        vidx = None

        if path in self._values[0]:
            idx = self._values[0].index(path)
        else:
            idx = None
        vidx = self._setvalue_info(0, idx, path, values, index, vidx)
        vidx = self._setvalue_info(1, idx, index, values, index, vidx)
        if isinstance(value, list):
            value = tuple(value)
        vidx = self._setvalue_info(2, idx, value, values, index, vidx)
        self._setvalue_info(3, idx, owner, values, index, vidx)
        self._values = tuple(values)

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
        # transform tuple to list
        values = list(self._values)
        values_idx = list(values[1])
        lvalues = list(values_idx[path_idx])
        # reduce to one the index
        lvalues[subidx] = lvalues[subidx] - 1
        # store modification
        values_idx[path_idx] = tuple(lvalues)
        values[1] = tuple(values_idx)
        self._values = tuple(values)

    def resetvalue_index(self,
                         path,
                         index,
                         commit):
        log.debug('resetvalue_index %s %s %s', path, index, id(self))
        def _resetvalue(nb):
            values_idx = list(values[nb])
            del(values_idx[path_idx])
            values[nb] = tuple(values_idx)

        def _resetvalue_index(nb):
            values_idx = list(values[nb])
            lvalues = list(values_idx[path_idx])
            del(lvalues[subidx])
            values_idx[path_idx] = tuple(lvalues)
            values[nb] = tuple(values_idx)

        path_idx = self._values[0].index(path)
        indexes = self._values[1][path_idx]
        if index in indexes:
            subidx = indexes.index(index)
            values = list(self._values)
            if len(values[1][path_idx]) == 1:
                _resetvalue(0)
                _resetvalue(1)
                _resetvalue(2)
                _resetvalue(3)
            else:
                _resetvalue_index(1)
                _resetvalue_index(2)
                _resetvalue_index(3)
            self._values = tuple(values)

    def resetvalue(self,
                   path,
                   commit):
        """remove value means delete value in storage
        """
        log.debug('resetvalue %s %s', path, id(self))
        def _resetvalue(nb):
            lst = list(self._values[nb])
            lst.pop(idx)
            values.append(tuple(lst))
        values = []
        if path in self._values[0]:
            idx = self._values[0].index(path)
            _resetvalue(0)
            _resetvalue(1)
            _resetvalue(2)
            _resetvalue(3)
            self._values = tuple(values)

    # owner
    def setowner(self,
                 path,
                 owner,
                 index=None):
        """change owner for a path
        """
        idx = self._values[0].index(path)
        if index is None:
            vidx = None
        else:
            vidx = self._values[1][idx].index(index)
        values = []
        self._setvalue_info(3, idx, owner, values, index, vidx)
        lst = list(self._values)
        lst[3] = tuple(values[0])
        self._values = tuple(lst)

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
        return self._values

    def importation(self, export):
        self._values = export


def delete_session(session_id):
    raise ValueError(_('cannot delete none persistent session'))
