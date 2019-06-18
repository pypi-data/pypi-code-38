# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This module contains the object manager class
"""

from abc import abstractproperty, abstractmethod
import re

from ... import exceptions
from ...abc.basemanager import BaseManager
from ...core.version import Version
from ...helpers import log


class ObjectManager(BaseManager):
    """
    Class for managing all the objects loaded in the fastr system
    """
    def __init__(self, path):
        """
        Create a ObjectManager and scan path to search for Objects

        :param path: the path(s) to scan for Objects
        :type path: str or iterable of str
        :return: newly created ObjectManager
        """
        super(ObjectManager, self).__init__(path, True)

    def __contains__(self, key):
        """
        Check if an item is in the ObjectManager

        :param key: object id or tuple (Objectid, version)
        :type key: str or tuple
        :return: flag indicating the item is in the manager
        """
        return self.__keytransform__(key) in self.data

    def __getitem__(self, key):
        """
        Retrieve a Object from the ObjectManager. You can request by only an id,
        which results in the newest version of the Object being returned, or
        request using both an id and a version.

        :param key: object id or tuple (Objectid, version)
        :type key: str or tuple
        :return: the requested Object
        :raises FastrObjectUnknownError: if a non-existing Object was requested
        """
        new_key = self.__keytransform__(key)
        if new_key not in self.data:
            raise exceptions.FastrObjectUnknownError('Key "{}" (expanded to {}) not found in {}'.format(key, new_key, type(self).__name__))

        obj = self.data[new_key]
        return obj

    def __keytransform__(self, key):
        """
        Key transform, used for allowing indexing both by id-only and by
        ``(id, version)``

        :param key: key to transform
        :return: key in form ``(id, version)``
        """
        # Get the version (or None)
        #if not isinstance(key, tuple):
        #    raise exceptions.FastrTypeError('Tool key must be a tuple of (str, tool_version)')

        #if not len(key) == 2:
        #    raise exceptions.FastrValueError('Tool must contain two elements (tool_str, tool_version)')
        #else:
        #    obj_str, obj_version = key

        #if isinstance(obj_str, str):
        #    log.info('Found obj_str: {}'.format(obj_str))
        #    match = re.match(r'^(.*?)/?([^/:]+):([^:]+)$', obj_str)
        #    if not match:
        #        raise exceptions.FastrValueError('Object key should be in form "item:version"')
        #    obj_namespace, object_id, version = match.groups()
        #    version = Version(version)
        #else:
        #    raise exceptions.FastrTypeError('Object key should be a string or tuple!')

        # Check that we are done (should be unique match)
        # return obj_namespace, '{}:{}'.format(object_id, version), version
        obj_id, obj_version = key

        if not isinstance(obj_version, Version):
            obj_version = Version(obj_version)

        return obj_id, obj_version

    @property
    def _item_extension(self):
        """
        Extension of files to load
        """
        return '(xml|json|yaml)'

    @abstractproperty
    def object_class(self):
        """
        The class of the objects to populate the manager with
        """

    @abstractmethod
    def get_object_version(self, obj):
        """
        Get the version of a given object

        :param object: the object to use
        :return: the version of the object
        """

    def _print_key(self, key):
        """
        Print function for the keys
        """
        return key[0], str(key[1])

    def _print_value(self, value):
        """
        Print function for the values
        """
        return value.filename

    def _load_item(self, filepath, namespace):
        """
        Load a Object file and store it in the Manager
        """
        obj = self.object_class.loadf(filepath)
        object_version = self.get_object_version(obj)

        # Make sure the last part of the directory structure is not the version
        # if that is the case, strip it
        if len(namespace) > 0:
            possible_version = namespace[-1]

            try:
                possible_version = Version(possible_version)
                if possible_version == object_version:
                    namespace = namespace[:-1]
            except exceptions.FastrVersionInvalidError:
                pass

        namespace = '/'.join(namespace)
        obj.namespace = namespace

        self._store_item((obj.ns_id, obj.version), obj)

    def todict(self):
        """
        Return a dictionary version of the Manager

        :return: manager as a dict
        """
        result = {}
        for key in self.keys():
            if key[0] not in result:
                result[key[0]] = []

            if str(key[1]) not in result[key[0]]:
                result[key[0]].append(str(key[1]))

        return result

    def objectversions(self, obj):
        """
        Return a list of available versions for the object

        :param object: The object to check the versions for. Can be either a `Object` or a `str`.
        :return: List of version objects. Returns `None` when the given object is not known.
        """

        if isinstance(obj, self.object_class):
            ns_id = obj.ns_id
        elif isinstance(obj, str):
            ns_id = obj

        log.info("Object namespaced id: {}".format(ns_id))

        return sorted(key[1] for key in self.keys() if key[0] == ns_id)
