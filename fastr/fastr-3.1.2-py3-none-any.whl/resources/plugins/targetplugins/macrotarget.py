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
The module containing the classes describing the targets.
"""

import imp

from fastr import exceptions, api
from fastr.core.target import Target


class MacroTarget(Target):
    """
    A target for MacroNodes. This target cannot be executed as the MacroNode handles
    execution differently. But this contains the information for the MacroNode to
    find the internal Network.
    """
    def __init__(self, network_file, method=None, function='main'):
        """
        Define a new local binary target. Must be defined either using paths and optionally environment_variables
        and initscripts, or enviroment modules.
        """
        # Figure out required method if not given
        if method is None:
            if network_file.endswith(('.py', '.pyc')):
                method = 'python'
            elif network_file.endswith(('.xml', '.json', 'yml', 'yaml')):
                method = 'loads'

        # Load the network
        if method == 'python':
            network_module = imp.load_source('macro_node.utils', network_file)
            network_function = getattr(network_module, function)
            network = network_function()
        elif method == 'loads':
            network = api.Network.load(network_file)
        else:
            raise exceptions.FastrValueError('Method {} is not know for a MacroTarget'.format(method))

        # Store the network parent
        if not network:
            raise exceptions.FastrValueError('Network not loaded correctly from "{}"'.format(network_file))
        self.network = network.parent

    @classmethod
    def test(cls):
        """
        Test if singularity is availble on the path
        """
        pass

    def run_command(self, command):
        raise exceptions.FastrNotImplementedError(
            'This method is purposefully not implemented, MacroTarget is not mean for direct execution'
        )
