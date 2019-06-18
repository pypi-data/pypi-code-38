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
This module contains the Manager class for Plugins in the fastr system
"""

import sys
from types import ModuleType


class LazyModule(ModuleType):
    """
    A module that allows content to be loaded lazily from plugins. It generally
    is (almost) empty and gets (partially) populated when an attribute cannot be
    found. This allows lazy loading and plugins depending on other plugins.
    """
    def __init__(self, name, parent, plugin_manager):
        super(LazyModule, self).__init__(name)
        self._plugin_manager = plugin_manager
        self.__dict__.update(vars(parent))
        self._parent = parent
        sys.modules[parent.__name__] = self

    def __repr__(self):
        return super(LazyModule, self).__repr__().replace('module', 'lazy_module', 1)

    def __getattr__(self, item):
        """
        The getattr is called when getattribute does not return a value and is
        used as a fallback. In this case we try to find the value normally and
        will trigger the plugin manager if it cannot be found.

        :param str item: attribute to retrieve
        :return: the requested attribute
        """
        try:
            return super(LazyModule, self).__getattribute__(item)
        except AttributeError as exception:
            try:
                return self._plugin_manager[item]
            except KeyError:
                raise exception
