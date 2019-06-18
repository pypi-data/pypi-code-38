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

import os
import subprocess

import fastr
from fastr import exceptions
from fastr.core.target import SubprocessBasedTarget


class SingularityTarget(SubprocessBasedTarget):
    """
    A tool target that is run using a singularity container,
    see the `singulary website <http://singularity.lbl.gov/>`_

    * ``binary (required)``: the name of the binary/script to call, can also be called ``bin``
      for backwards compatibility.
    * ``container (required)``: the singularity container to run, this can be in url form for singularity
                                pull or as a path to a local container

    * ``interpreter``: the interpreter to use to call the binary e.g. ``python``

    """
    SINGULARITY_BIN = 'singularity'

    def __init__(self, binary, container, interpreter=None):
        """
        Define a new local binary target. Must be defined either using paths and optionally environment_variables
        and initscripts, or enviroment modules.
        """
        self.binary = binary
        self.container = container
        self.interpreter = interpreter

    def __enter__(self):
        """
        Set the environment in such a way that the target will be on the path.
        """
        super(SingularityTarget, self).__enter__()

        # TODO Make sure the container is present, otherwise download the container
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Cleanup the environment
        """
        # TODO We could potentially remove the container again if we downloaded it in the first place?
        pass

    @classmethod
    def test(cls):
        """
        Test if singularity is availble on the path
        """
        try:
            subprocess.check_output([cls.SINGULARITY_BIN, '--help'], stderr=subprocess.STDOUT)
        except OSError:
            raise exceptions.FastrExecutableNotFoundError(cls.SINGULARITY_BIN)

    def run_command(self, command):
        # Add interpreter if needed
        if self.interpreter is not None:
            command = [self.interpreter] + command

        # Bind all fastr mounts
        mounts = fastr.config.mounts.values()
        binds = []
        for mount in mounts:
            if not os.path.exists(mount):
                continue

            binds.append('--bind')
            binds.append('{x}:{x}'.format(x=mount))

        fastr.log.info('Singularity binds: {}'.format(binds))

        # Compose the singularity command
        singularity_command = [self.SINGULARITY_BIN, 'exec']
        singularity_command.extend(binds)
        singularity_command.append(self.container)
        singularity_command.extend(command)

        # Create final command
        fastr.log.debug('Command: {}'.format(command))
        fastr.log.debug('Singularity command: {}'.format(singularity_command))
        return self.call_subprocess(singularity_command)
