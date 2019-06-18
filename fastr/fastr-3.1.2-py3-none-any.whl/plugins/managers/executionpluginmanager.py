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
This module holds the ExecutionPluginManager as well as the base-class
for all ExecutionPlugins.
"""

from .pluginmanager import PluginSubManager
from ..executionplugin import ExecutionPlugin


class ExecutionPluginManager(PluginSubManager):
    """
    Container holding all the ExecutionPlugins known to the Fastr system
    """

    def __init__(self, parent):
        """
        Initialize a ExecutionPluginManager and load plugins.

        :param path: path to search for plugins
        :param recursive: flag for searching recursively
        :return: newly created ExecutionPluginManager
        """
        super(ExecutionPluginManager, self).__init__(parent=parent,
                                                     plugin_class=ExecutionPlugin)

    @property
    def _instantiate(self):
        """
        Indicate that the plugins should not instantiated before being stored
        """
        return False
