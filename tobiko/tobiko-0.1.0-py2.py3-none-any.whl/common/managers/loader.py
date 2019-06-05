# Copyright 2019 Red Hat
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from __future__ import absolute_import

import importlib
import inspect
import weakref
import sys


def load_object(object_id, manager=None, new_loader=None, cached=True):
    manager = manager or LOADERS
    loader = manager.get_loader(object_id=object_id, new_loader=new_loader)
    return loader.load(manager=manager, cached=cached)


def load_module(object_id, manager=None, new_loader=None, cached=True):
    manager = manager or LOADERS
    loader = manager.get_loader(object_id=object_id, new_loader=new_loader)
    return loader.load_module(manager=manager, cached=cached)


class ObjectLoader(object):
    """Previously loaded object meta-data"""

    # Weak reference to target object
    _ref = None

    # Flag that tells if referenced object is an imported module
    _is_module = None

    def __init__(self, object_id):
        # Object ID
        self._id = object_id
        if '.' in object_id:
            # Extract object name and parent id from object id
            parent_id, name = object_id.rsplit('.', 1)
            self._name = name
            self._parent_id = parent_id
        else:
            # Root objects have no parent
            self._name = object_id
            self._parent_id = None

    @property
    def is_module(self):
        return self._is_module

    @property
    def id(self):
        return self._id

    def set(self, obj):
        if obj is None:
            self._is_module = False
            self.get = self._get_none
        elif inspect.ismodule(obj):
            # Cannot create weak reference to modules on Python2
            self._is_module = True
            self.get = self._get_module
        else:
            self._is_module = False
            self._ref = weakref.ref(obj)
            self.get = self._get_object

    def __repr__(self):
        return '{cls!s}({id!r})'.format(cls=type(self).__name__, id=self._id)

    def _get_not_cached(self):
        msg = "Object {!r} not cached".format(self._id)
        raise RuntimeError(msg)

    get = _get_not_cached

    @staticmethod
    def _get_none():
        return None

    def _get_module(self):
        try:
            return sys.modules[self._id]
        except KeyError:
            pass
        return self._get_not_cached()

    def _get_object(self):
        obj = self._ref()
        if obj is None:
            return self._get_not_cached()
        return obj

    def load(self, manager, cached=True):
        if cached:
            try:
                return self.get()
            except RuntimeError:
                pass

        parent_loader = self.get_parent(manager=manager)
        if parent_loader:
            parent = parent_loader.load(manager=manager, cached=cached)
            name = self._name
            try:
                obj = getattr(parent, name)
            except AttributeError:
                if parent_loader.is_module:
                    return self._load_module()
                else:
                    # Child cannot be a module if parent isn't a module
                    raise
            else:
                self.set(obj)
                return obj
        else:
            # Root objects can only be modules
            return self._load_module()

    def _load_module(self):
        obj = importlib.import_module(self._id)
        self.set(obj)
        return obj

    def get_parent(self, manager):
        parent_id = self._parent_id
        if parent_id:
            return manager.get_loader(object_id=parent_id)
        else:
            return None

    def load_module(self, manager, cached=True):
        if cached and self._is_module:
            return self.get()

        self.load(manager=manager, cached=cached)
        if self._is_module:
            return self.get()

        parent = self.get_parent(manager=manager)
        if parent:
            return parent.load_module(manager=manager, cached=True)

        msg = ("Non-module object {!r} has no parent").format(self._id)
        raise RuntimeError(msg)


class LoaderManager(object):

    def __init__(self):
        # Dictionary used to cache object references
        self._loaders = {}

    new_loader = ObjectLoader

    def get_loader(self, object_id, new_loader=None):
        """Get existing ObjectInfo or create new one

        It implements singleton pattern by caching previously created
        ObjectInfo instances to OBJECT_INFOS for later retrieval
        """
        try:
            return self._loaders[object_id]
        except KeyError:
            pass

        new_loader = new_loader or self.new_loader
        loader = new_loader(object_id=object_id)
        if not isinstance(loader, ObjectLoader):
            msg = "{!r} is not instance of class ObjectLoader".format(loader)
            raise TypeError(msg)

        self._loaders[object_id] = loader
        return loader


LOADERS = LoaderManager()
