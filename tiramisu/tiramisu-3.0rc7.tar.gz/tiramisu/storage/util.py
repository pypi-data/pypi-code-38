# -*- coding: utf-8 -*-
"utils used by storage"
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
from time import time
from .cache.dictionary import Cache as DictCache
from ..log import log


def _display_classname(obj):  # pragma: no cover
    return(obj.__class__.__name__.lower())


class Cache(DictCache):
    __slots__ = ('_storage',)

    def __init__(self, storage):
        self._storage = storage
        super().__init__()

    def setcache(self, path, index, val, self_props, props):
        """add val in cache for a specified path
        if follower, add index
        """
        if 'cache' in props or 'cache' in self_props:
            log.debug('setcache {} with index {} and value {} in {} ({})'.format(path, index, val,
                                                                                 _display_classname(self),
                                                                                 id(self)))
            self._setcache(path, index, val, time())
        log.debug('not setcache {} with index {} and value {} and props {} and {} in {} ({})'.format(path,
                                                                                                     index,
                                                                                                     val,
                                                                                                     props,
                                                                                                     self_props,
                                                                                                     _display_classname(self),
                                                                                                     id(self)))

    def getcache(self,
                 path,
                 expiration_time,
                 index,
                 props,
                 self_props,
                 type_):
        no_cache = False, None
        if 'cache' in props or type_ == 'context_props':
            indexed = self._getcache(path, index)
            if indexed is None:
                return no_cache
            value, timestamp = indexed
            if type_ == 'context_props':
                # cached value is settings properties so value is props
                props = value
            elif type_ == 'self_props':
                # if self_props is None, so cached value is self properties
                # so value is self_props
                self_props = value
            # recheck "cache" value
            if 'cache' in props or 'cache' in props:
                if expiration_time and timestamp and \
                        ('expire' in props or \
                         'expire' in self_props):
                    ntime = int(time())
                    if timestamp + expiration_time >= ntime:
                        log.debug('getcache in cache (1) %s %s %s %s %s', path, value, _display_classname(self),
                                  id(self), index)
                        return True, value
                    #else:
                    #    log.debug('getcache expired value for path {} < {}'.format(
                    #              timestamp + expiration_time, ntime))
                    #    # if expired, remove from cache
                    #    #self.delcache(path)
                else:
                    log.debug('getcache in cache (2) %s %s %s %s %s', path, value, _display_classname(self),
                              id(self), index)
                    return True, value
        log.debug('getcache {} with index {} not in {} cache'.format(path, index,
                                                                     _display_classname(self)))
        return no_cache

    def delcache(self, path):
        """remove cache for a specified path
        """
        log.debug('delcache %s %s %s', path, _display_classname(self), id(self))
        if path in  self._cache:
            self._delcache(path)

    def reset_all_cache(self):
        "empty the cache"
        log.debug('reset_all_cache %s %s', _display_classname(self), id(self))
        self._reset_all_cache()

    def get_cached(self):
        """return all values in a dictionary
        please only use it in test purpose
        example: {'path1': {'index1': ('value1', 'time1')}, 'path2': {'index2': ('value2', 'time2', )}}
        """
        log.debug('get_chached {} for {} ({})'.format(self._cache, _display_classname(self), id(self)))
        return self._get_cached()
