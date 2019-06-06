"""
Copyright 2018 Cognitive Scale, Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import pickle
from IPython.core.magic import (Magics, magics_class, cell_magic)
from IPython.utils._process_common import arg_split

from types import ModuleType
import argparse

from . import Cortex
from .logger import getLogger

log = getLogger(__name__)


_shim = """
def main(params):
    return %s(params)
"""


def strip_quotes(s: str):
    """
    Remove quotes from a string.
    """
    if not s: return ''
    return s.strip().replace('"', '').replace("'", '')


@magics_class
class CortexMagics(Magics):
    """
    Magic functions for Cortex.
    """
    @cell_magic
    def cortex_action(self, line, cell):
        """
        Provides cell magic for a Cortex action.
        """
        script_text = []
        pickleable_ns = {}

        self.shell.run_cell(cell)

        for varname, var in self.shell.user_ns.items():
            if not varname.startswith('__'):
                if isinstance(var, ModuleType) and var.__name__ != 'cortex.magics':
                    script_text.append(
                        'import {} as {}'.format(var.__name__, varname)
                    )
                else:
                    try:
                        pickle.dumps(var)
                        pickleable_ns[varname] = var
                    except BaseException:
                        pass

        script_text.append(cell)

        parser = argparse.ArgumentParser(description='cortex_action')
        parser.add_argument('--name', action='store', type=str)
        parser.add_argument('--function', action='store', type=str)
        parser.add_argument('--registry', action='store', type=str)
        parser.add_argument('--prefix', action='store', type=str)
        parser.add_argument('--requirements', action='store', type=str)
        parser.add_argument('--conda-requirements', action='store', type=str)
        parser.add_argument('--freeze', action='store_true')
        parser.add_argument('--debug', action='store_true')
        parser.add_argument('--daemon', action='store_true')
        parser.add_argument('--job', action='store_true')
        parser.add_argument('--writefile', action='store', type=str)
        parser.add_argument('--base-image', action='store', type=str)

        args = arg_split(line)
        opts = parser.parse_args(args)

        if not opts.name:
            raise Exception('"name" is a required property for Cortex Actions')

        if opts.function:
            script_text.append(_shim % strip_quotes(opts.function))

        cortex = Cortex.client()
        builder = cortex.builder()

        script_text = '\n'.join(script_text)
        if opts.debug:
            print('cortex_action %s' % line)
            print(script_text)

        b = builder.action(strip_quotes(opts.name))

        # Set the Docker registry URI to use
        if opts.registry:
            b.registry(opts.registry)
        # Set the Docker image prefix to use if set and only if the registry URI is not specified
        elif opts.prefix:
            b.image_prefix(opts.prefix)
            b.from_image(opts.name)

        if opts.daemon:
            b.daemon()

        if opts.job:
            b.job()

        if opts.requirements:
            reqs = opts.requirements.split(',')
            b.with_requirements(reqs)

        if opts.conda_requirements:
            reqs = opts.conda_requirements.split(',')
            b.with_conda_requirements(reqs)

        if opts.freeze:
            b.with_pip_freeze()

        if opts.base_image:
            b.with_base_image(opts.base_image)

        action = b.from_source(script_text).build()

        print('Action deployed')

        if opts.writefile:
            try:
                print('Writing file {}...'.format(opts.writefile))
                with open(opts.writefile, 'w') as f:
                    f.write(cell)
            except IOError as e:
                print('Failed to write file: {}'.format(e.message))
                log.error('Failed to write file: {}'.format(e.message))

        return action
