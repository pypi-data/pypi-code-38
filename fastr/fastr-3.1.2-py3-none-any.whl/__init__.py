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

FASTR is a top level package which includes all parts required to create
networks and edit networks.
"""

__all__ = [
    'create_network',
    'create_network_copy',
    'config',
    'datatypes',
    'exceptions',
    'networks',
    'plugins',
    'tools',
    'types',
    'vfs'
]
# In the top level module we want to add some variables which are constants
# but use a non-constant name (not caps)
# pylint: disable=invalid-name

from colorama import init
init()

# Get version info
from . import version, exceptions
__version__ = version.version

#: Configuration and logging of the fastr system
from .helpers import config
from .helpers import log

from .api import create_network, create_network_copy

from .helpers.lazy_module import LazyModule


# Import data types and create a lazy loading module for that
from . import datatypes
types = datatypes.types
datatypes = LazyModule("datatypes", parent=datatypes, plugin_manager=types)

# Import plugins and create a lazy loading module for that
from . import plugins
plugin_manager = plugins.plugins
plugins = LazyModule("plugins", parent=plugins, plugin_manager=plugins.plugins)
plugin_manager.set_module(plugins)

# Load resources for tools and networks
from .resources import tools, networks

# The following loads all ioplugins from the resources folder and registers the built-in vfs with the plugin list
from .core import vfs_plugin as vfs

log.debug('Finished with the FASTR environment set up')


# Warn if this is not a neatly installed package from the stable branch
if config.warn_develop and (version.not_default_branch or version.from_mercurial):
    log.warning('Not running in a production installation (branch "{}" from {})'.format(
        version.hg_branch,
        'source code' if version.from_mercurial else 'installed package'
    ))
