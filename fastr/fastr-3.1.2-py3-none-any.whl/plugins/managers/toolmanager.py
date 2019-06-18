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
This module contains the tool manager class
"""

from .objectmanager import ObjectManager
from .iopluginmanager import IOPluginManager
from ...core.tool import Tool
from ... import resources


class ToolManager(ObjectManager):
    def populate(self):
        super().populate()
        IOPluginManager.create_ioplugin_tool(self, interfaces=resources.interfaces)

    @property
    def object_class(self):
        return Tool

    def get_object_version(self, obj):
        return obj.command['version']

    def toolversions(self, tool):
        """
        Return a list of available versions for the tool

        :param tool: The tool to check the versions for. Can be either a `Tool` or a `str`.
        :return: List of version objects. Returns `None` when the given tool is not known.
        """
        return self.objectversions(tool)
