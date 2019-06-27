#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT: a jabber client
# Copyright (C) 2009-2019 Jérôme Poisson (goffi@goffi.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from sat.core.i18n import _
from sat.core.log import getLogger
log = getLogger(__name__)
from twisted.python import failure


class MemoryNotInitializedError(Exception):
    pass


class PersistentDict(object):
    r"""A dictionary which save persistently each value assigned

    /!\ be careful, each assignment means a database write
    /!\ Memory must be initialised before loading/setting value with instances of this class"""
    storage = None
    binary = False

    def __init__(self, namespace, profile=None):
        """

        @param namespace: unique namespace for this dictionary
        @param profile(unicode, None): profile which *MUST* exists, or None for general values
        """
        if not self.storage:
            log.error(_("PersistentDict can't be used before memory initialisation"))
            raise MemoryNotInitializedError
        self._cache = {}
        self.namespace = namespace
        self.profile = profile

    def _setCache(self, data):
        self._cache = data

    def load(self):
        """Load persistent data from storage.

        need to be called before any other operation
        @return: defers the PersistentDict instance itself
        """
        d = self.storage.getPrivates(self.namespace, binary=self.binary, profile=self.profile)
        d.addCallback(self._setCache)
        d.addCallback(lambda __: self)
        return d

    def iteritems(self):
        return self._cache.iteritems()

    def items(self):
        return self._cache.items()

    def __repr__(self):
        return self._cache.__repr__()

    def __str__(self):
        return self._cache.__str__()

    def __lt__(self, other):
        return self._cache.__lt__(other)

    def __le__(self, other):
        return self._cache.__le__(other)

    def __eq__(self, other):
        return self._cache.__eq__(other)

    def __ne__(self, other):
        return self._cache.__ne__(other)

    def __gt__(self, other):
        return self._cache.__gt__(other)

    def __ge__(self, other):
        return self._cache.__ge__(other)

    def __cmp__(self, other):
        return self._cache.__cmp__(other)

    def __hash__(self):
        return self._cache.__hash__()

    def __nonzero__(self):
        return self._cache.__len__()

    def __contains__(self, key):
        return self._cache.__contains__(key)

    def __iter__(self):
        return self._cache.__iter__()

    def __getitem__(self, key):
        return self._cache.__getitem__(key)

    def __setitem__(self, key, value):
        self.storage.setPrivateValue(self.namespace, key, value, self.binary,
                                     self.profile)
        return self._cache.__setitem__(key, value)

    def __delitem__(self, key):
        self.storage.delPrivateValue(self.namespace, key, self.binary, self.profile)
        return self._cache.__delitem__(key)

    def clear(self):
        """Delete all values from this namespace"""
        self._cache.clear()
        return self.storage.delPrivateNamespace(self.namespace, self.binary, self.profile)

    def get(self, key, default=None):
        return self._cache.get(key, default)

    def setdefault(self, key, default):
        try:
            return self._cache[key]
        except:
            self.__setitem__(key, default)
            return default

    def force(self, name):
        """Force saving of an attribute to storage

        @return: deferred fired when data is actually saved
        """
        return self.storage.setPrivateValue(self.namespace, name, self._cache[name],
                                            self.binary, self.profile)


class PersistentBinaryDict(PersistentDict):
    """Persistent dict where value can be any python data (instead of string only)"""
    binary = True


class LazyPersistentBinaryDict(PersistentBinaryDict):
    ur"""PersistentBinaryDict which get key/value when needed

    This Persistent need more database access, it is suitable for largest data,
    to save memory.
    /!\ most of methods return a Deferred
    """
    # TODO: missing methods should be implemented using database access
    # TODO: a cache would be useful (which is deleted after a timeout)

    def load(self):
        # we show a warning as calling load on LazyPersistentBinaryDict sounds like a code mistake
        log.warning(_(u"Calling load on LazyPersistentBinaryDict while it's not needed"))

    def iteritems(self):
        raise NotImplementedError

    def items(self):
        return self.storage.getPrivates(self.namespace, binary=self.binary, profile=self.profile)

    def __repr__(self):
        raise NotImplementedError

    def __str__(self):
        return "LazyPersistentBinaryDict (namespace: {})".format(self.namespace)

    def __lt__(self, other):
        raise NotImplementedError

    def __le__(self, other):
        raise NotImplementedError

    def __eq__(self, other):
        raise NotImplementedError

    def __ne__(self, other):
        raise NotImplementedError

    def __gt__(self, other):
        raise NotImplementedError

    def __ge__(self, other):
        raise NotImplementedError

    def __cmp__(self, other):
        raise NotImplementedError

    def __hash__(self):
        return hash(unicode(self.__class__) + self.namespace + (self.profile or u''))

    def __nonzero__(self):
        raise NotImplementedError

    def __contains__(self, key):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    def _data2value(self, data, key):
        try:
            return data[key]
        except KeyError as e:
            # we return a Failure here to avoid the jump
            # into debugger in debug mode.
            raise failure.Failure(e)

    def __getitem__(self, key):
        """get the value as a Deferred"""
        d = self.storage.getPrivates(self.namespace, keys=[key], binary=self.binary,
                                     profile=self.profile)
        d.addCallback(self._data2value, key)
        return d

    def __setitem__(self, key, value):
        self.storage.setPrivateValue(self.namespace, key, value, self.binary,
                                     self.profile)

    def __delitem__(self, key):
        self.storage.delPrivateValue(self.namespace, key, self.binary, self.profile)

    def _defaultOrException(self, failure_, default):
        failure_.trap(KeyError)
        return default

    def get(self, key, default=None):
        d = self.__getitem__(key)
        d.addErrback(self._defaultOrException, default=default)
        return d

    def setdefault(self, key, default):
        raise NotImplementedError

    def force(self, name, value):
        """Force saving of an attribute to storage

        @param value(object): value is needed for LazyPersistentBinaryDict
        @return: deferred fired when data is actually saved
        """
        return self.storage.setPrivateValue(self.namespace, name, value, self.binary, self.profile)

    def remove(self, key):
        """Delete a key from sotrage, and return a deferred called when it's done

        @param key(unicode): key to delete
        @return (D): A deferred fired when delete is done
        """
        return self.storage.delPrivateValue(self.namespace, key, self.binary, self.profile)
