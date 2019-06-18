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
This module contains the core class for all plugins.managers
"""

from collections.abc import MutableMapping, Iterable
import os
import re
import sys
import traceback
from abc import ABCMeta, abstractmethod, abstractproperty
from fastr.exceptions import FastrKeyError, FastrNotImplementedError
import fastr


class BaseManager(MutableMapping):
    """
    Baseclass for a Manager, subclasses needs to override the following methods:
      BaseManager._item_extension, BaseManager._load_item()

    .. automethod:: _item_extension

    .. automethod:: _load_item
    """

    def __init__(self, path=None, recursive=False):
        """
        The BaseManager constructor

        :param path: path to scan for items, or None for no path
        :type path: str or None
        :param bool recursive: Flag to indicate a recursive search is desired
        :return: the newly created BaseManager
        :rtype: BaseManager
        """
        self._scanned_directories = []
        self._path = (path, recursive)
        self._data = None

    @property
    def data(self):
        """
        The actual data dict underlying this Manager
        """
        if self._data is None:
            self.populate()

        return self._data

    def populate(self):
        """
        Populate the manager with the data. This is a method that will be
        called when the Managers data is first accessed. This way we avoid
        doing expensive directory scans when the data is never requested.
        """
        self._data = dict()
        if self._path[0] is not None:
            self._scan_directory(self._path[0], recursive=self._path[1])

    def reload(self):
        """
        Reload entire contents of this manager.
        """
        self.clear()
        self.populate()

    def __repr__(self):
        """
        Convert the BaseManager to a representation string.

        :return: Representation string
        :rtype: str
        """
        if len(self) == 0:
            return 'Empty {}'.format(type(self).__name__)

        keylist = [self._print_key(x) for x in self.keys()]
        if isinstance(keylist[0], tuple):
            width = zip(*keylist)
            width = [max([len(str(x)) for x in y]) for y in width]
            format_base_key = '  '.join(['{{key[{n}]:<{width}}}'.format(n=n, width=w) for n, w in enumerate(width)])
        else:
            width = max([len(str(x)) for x in keylist if x is not None])
            format_base_key = '{{key:<{width}}}'.format(width=width)

        valuelist = [self._print_value(x) for x in self.values()]
        if isinstance(valuelist[0], tuple):
            width = zip(*valuelist)
            width = [max([len(str(x)) for x in y]) for y in width]
            format_base_value = '  '.join(['{{val[{n}]:<{width}}}'.format(n=n, width=w) for n, w in enumerate(width)])
        else:
            width = max([len(str(x)) for x in valuelist])
            format_base_value = '{{val:<{width}}}'.format(width=width)

        output = [type(self).__name__]
        format_base = '{}  :  {}'.format(format_base_key, format_base_value)

        for key, val in sorted(self.items()):
            key = self._print_key(key)
            if key is not None:
                output.append(format_base.format(key=key, val=self._print_value(val)))

        return '\n'.join(output)

    def __getitem__(self, key):
        """
        Retrieve item from BaseManager

        :param key: the key of the item to retrieve
        :return: the value indicated by the key
        :raises FastrKeyError: if the key is not found in the BaseManager
        """
        transformed_key = self.__keytransform__(key)
        if transformed_key not in self.data:
            raise FastrKeyError('Object "{}" ("{}") not found in {}'.format(key,
                                                                            transformed_key,
                                                                            type(self).__name__))

        return self.data[transformed_key]

    def __setitem__(self, key, value):
        """
        Set item in the BaseManager

        :param key: the key of the item to store
        :param value: the value of the item to store
        :return: None
        """
        self.data[self.__keytransform__(key)] = value

    def __delitem__(self, key):
        """
        Remove item from the BaseManager

        :param key: key of the item to remove
        :return: None
        :raises FastrKeyError: if the key is not found in the BaseManager
        """

        if key not in self.data:
            raise FastrKeyError('Plugin "{}" not found in {}'.format(key, type(self).__name__))

        del self.data[self.__keytransform__(key)]

    def __iter__(self):
        """
        Get an iterator from the BaseManager. The iterator will iterate over
        the keys of the BaseManager.

        :return: the iterator
        :rtype: dictionary-keyiterator
        """
        return iter(self.data)

    def __len__(self):
        """
        Return the number of items in the BaseManager

        :return: number of items in the BaseManager
        :rtype: int
        """
        return len(self.data)

    def __keytransform__(self, key):
        """
        Identity transform for the keys. This function can be reimplemented by
        a subclass to implement a different key transform.

        :param key: key to transform
        :return: the transformed key (in this case the same key as inputted)
        """
        return key

    def _print_key(self, key):
        """
        Return a printable version of the key

        :param key: the key to convert
        :return: printable version of the key
        :rtype: str
        """
        return str(key)

    def _print_value(self, val):
        """
        Return a printable version of the value

        :param key: the value to convert
        :return: printable version of the value
        :rtype: str
        """
        return str(val)

    @abstractproperty
    def _item_extension(self):
        """
        Abstract property that sets the extension of the files to be loaded by
        the BaseManager. When scanning for items, only files with this
        extension will be loaded.

        :return: desired extension
        :rtype: str
        :raises FastrNotImplementedError: if property not reimplemented in subclass
        """
        raise FastrNotImplementedError("Purposefully not implemented!")

    def match_filename(self, filename):
        """
        Check if the filename matches the pattern the manager expects.

        :param filename: filename to match
        :return: flag indicating that the filename matches
        """
        extension = self._item_extension
        if extension.startswith('.'):
            extension = '\\{}'.format(extension)
        elif not extension.startswith('\\.'):
            extension = '\\.{}'.format(extension)

        pattern = "^.*{}$".format(extension)
        result = re.match(pattern, filename)
        fastr.log.debug('Matching {} with {} -> {}'.format(filename, pattern, result))
        return result is not None

    @abstractmethod
    def _load_item(self, filepath, namespace):
        """
        Abstract method to load an item of the BaseManager. This function is
        not implemented and needs to be reimplemented by a subclass.

        :param str filepath: path of the item to load
        :param str namespace: the namespace of the item to be loaded
        :return: the loaded item
        :raises FastrNotImplementedError: if called without being reimplemented by a subclass
        """
        raise FastrNotImplementedError("Purposefully not implemented!")

    def _store_item(self, name, value):
        """
        Store an item in the BaseManager, will ignore the item if the key is
        already present in the BaseManager.

        :param name: the key of the item to save
        :param value: the value of the item to save
        :return: None
        """

        # Do not check name in self, this will be very inefficient!
        if name in list(self.keys()):
            fastr.log.warning('Skipping {} from {} (the plugin is already in the {})'.format(
                name, value.filename, type(self).__name__)
            )
        else:
            fastr.log.debug('Loaded {} {} from {}'.format(type(value).__name__, name, value.filename))
            self[name] = value

    def _scan_directory(self, path, recursive=False, namespace=None):
        """
        Scan a directory for items of the BaseManager to load. All files in a
        directory will be checked. If the extension matches the
        BaseManager._item_extension it will be loaded and added to the
        BaseManager.

        :param str path: path to scan
        :param bool recursive: indicate whether or not to scan the directory recursively
        :return: None
        """
        # Unpack lists, tuples, deques and other objects with a valid __iter__
        if not isinstance(path, str) and isinstance(path, Iterable):
            for entry in path:
                self._scan_directory(entry, recursive)
        else:
            if not os.path.exists(path):
                fastr.log.warning('Cannot scan {} with {}, path does not exist!'.format(path, type(self).__name__))
                return

            if namespace is None:
                namespace = ()

            # Scan directory
            self._scanned_directories.append(path)
            fastr.log.debug('{} scanning {} (recursive={})'.format(type(self).__name__, path, recursive))
            for filename in os.listdir(path):
                filepath = os.path.join(path, filename)

                if os.path.isdir(filepath):
                    if recursive:
                        self._scan_directory(filepath, recursive, namespace + (filename,))
                elif os.path.isfile(filepath) and self.match_filename(filename):
                    if filename.startswith('__'):
                        continue

                    # Since we cannot know what Plugins might throw, catch all
                    # pylint: disable=bare-except
                    try:
                        self._load_item(filepath, namespace=namespace)
                    except Exception as exception:
                        fastr.log.warning('Could not load file {}: {}'.format(filepath, exception))
                        exc_type, _, _ = sys.exc_info()
                        exc_info = traceback.format_exc()
                        fastr.log.debug('Encountered exception ({}) during loading:\n{}'.format(
                            exc_type.__name__, exc_info)
                        )
                        raise
