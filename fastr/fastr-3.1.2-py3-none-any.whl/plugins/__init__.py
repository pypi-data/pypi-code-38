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
The plugins module holds all plugins loaded by Fastr. It is empty on start
and gets filled by the BasePluginManager
"""

from ..helpers import config

from .managers.pluginmanager import PluginManager
from .managers.executionpluginmanager import ExecutionPluginManager
from .managers.interfacemanager import InterfacePluginManager
from .managers.iopluginmanager import IOPluginManager
from .managers.targetmanager import TargetManager

from .managers.toolmanager import ToolManager
from .managers.networkmanager import NetworkManager

from .. import resources

# Main plugin manager
plugins = PluginManager()

# All the submanagers for specific access
execution_plugins = ExecutionPluginManager(plugins)
interfaces = InterfacePluginManager(plugins)
ioplugins = IOPluginManager(plugins)
targets = TargetManager(plugins)

# Create the toollist
tools = ToolManager(config.tools_path)

# Creat the network list
networklist = NetworkManager(config.networks_path)

# Register resources
resources.plugins = plugins
resources.execution_plugins = execution_plugins
resources.interfaces = interfaces
resources.ioplugins = ioplugins
resources.targets = targets

resources.tools = tools
resources.networks = networklist
