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
This module contains a class to interact with EnvironmentModules
"""

import os
import re
import subprocess

from enum import Enum

from .. import exceptions
from ..helpers import log
from ..helpers.procutils import which


class ModuleSystem(Enum):
    lmod = 'Lmod'
    envmod = 'enviromentmodules'


class EnvironmentModules(object):
    """
    This class can control the module environments in python. It can list, load
    and unload environmentmodules. These modules are then used if subprocess is
    called from python.
    """

    try:
        # Do the initialization of Environment Modules of the system
        if 'MODULESHOME' not in os.environ:
            raise exceptions.FastrImportError('Cannot find Environment Modules home directory (environment variables not setup properly?)')

        if 'MODULE_VERSION' not in os.environ:
            os.environ['MODULE_VERSION_STACK'] = '3.2.6'
            os.environ['MODULE_VERSION'] = '3.2.6'
        else:
            os.environ['MODULE_VERSION_STACK'] = os.environ['MODULE_VERSION']

        if 'MODULEPATH' not in os.environ:
            try:
                __paths = []
                with open(os.path.join(os.environ['MODULESHOME'], 'init', '.modulespath'), 'r') as fin:
                    for line in fin:
                        line = re.sub(r'(?P<path>[^#]*)(\#.*)', '\\g<path>', line).strip()
                        if line:
                            __paths.append(line)
            except:
                raise exceptions.FastrImportError('Cannot load Environment Modules path defintion!')

            os.environ['MODULEPATH'] = ':'.join(__paths)

        if 'LOADEDMODULES' not in os.environ:
            os.environ['LOADEDMODULES'] = ''

        if 'LMOD_CMD' in os.environ:
            # Lua mod is installed, we prefer lua mod
            _bin = os.environ['LMOD_CMD']
            _module_settings_system = ModuleSystem.lmod
        else:
            # The old environment modules is installed
            _bin = '{}/bin/modulecmd'.format(os.environ['MODULESHOME'])
            _module_settings_system = ModuleSystem.envmod

        if not os.path.isfile(_bin) or not os.access(_bin, os.X_OK):
            _bin = which('modulecmd')
            if _bin is None:
                raise exceptions.FastrImportError('Cannot find Environment Modules executable!')

    except exceptions.FastrImportError as exception:
        _module_settings_loaded = False
        _module_settings_warning = exception.message
    else:
        _module_settings_loaded = True
        _module_settings_warning = ''

    def __init__(self, protected=None):
        """
        Create the environmentmodules control object

        :param list protected: list of modules that should never be unloaded
        :return: newly created EnvironmentModules
        """
        if not self._module_settings_loaded:
            raise exceptions.FastrValueError('Could not load the environmentmodules settings during import, this module is non-functional! Original exception: {}'.format(self._module_settings_warning))

        # Debug print the system used
        log.debug('Using the {} system'.format(self._module_settings_system))

        # Set initial versions
        self._avail_string = ''
        self._avail_modules = ()
        self._loaded_modules = ()

        # Sync all available and loaded Modules
        self.sync()

        if protected is not None:
            self._protected = protected
        else:
            self._protected = []

    def __repr__(self):
        return "<EnvironmentModules system={}>".format(self._module_settings_system)

    def sync(self):
        """
        Sync the object with the underlying environment. Re-checks the
        available and loaded modules
        """
        self._sync_loaded()
        self._sync_avail()

    def _sync_loaded(self):
        """
        Sync the loaded modules with the underlying environmentmodules
        """
        _, stderr = self._module('list')

        loaded_modules = []
        for line in stderr.splitlines():
            for module in re.findall(r'\W*(\d+)\) ([\w\-\.]+)(/[^\(^\)^ ^\t]+)?', line):
                loaded_modules.append(module)

        # Sort and remove order from tuples
        loaded_modules.sort()
        loaded_modules = [module[1:] for module in loaded_modules]

        self._loaded_modules = tuple(loaded_modules)

    def _sync_avail(self):
        """
        Sync the available modules with the underlying environmentmodules
        """
        _, self._avail_string = self._module('avail')

        modules = []
        for line in self._avail_string.split('\n'):
            # Skip padding lines etc
            if len(line) == 0 or line[0] == '-' or '/' not in line:
                continue

            # Parse the line
            for part in line.split():
                if part == '(L)':
                    continue

                if part == '(D)':
                    modules[-1] = modules[-1][:-1] + (True,)
                    continue

                if part.endswith('(default)'):
                    default = True
                    part = part[:-9]
                else:
                    default = False

                modules.append(tuple(part.split('/') + [default]))

        # Sort modules by name/version
        modules.sort()

        self._avail_modules = tuple(modules)

    def _module(self, *arguments):
        """
        Call the environmentmodule executable

        :param arguments: arguments similar to the commandline version
        :return: tuple with (stdout, stderr)
        """
        args = [self._bin, 'python']
        args.extend(arguments)
        proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()

        return stdout.decode('utf-8'), stderr.decode('utf-8')

    @staticmethod
    def totuple_modvalue(value):
        """
        Turn a representation of a module into a tuple representation

        :param value: module representation (either str or tuple)
        :return: tuple representation (name, version, default)
        """
        if isinstance(value, str):
            match = re.match(r'([^/^\(^\)]+)([^\(^\)^ ^\t]+)?(\(default\))?', value)
            if match:
                value = match.groups()
                return value[:-1]
            else:
                raise exceptions.FastrValueError('Invalid module string ({})!'.format(value))
        elif isinstance(value, tuple):
            if len(value) in [2, 3]:
                return value
            else:
                raise exceptions.FastrValueError('Invalid module tuple ({})!'.format(value))
        else:
            raise exceptions.FastrTypeError('Invalid module value type ({})!'.format(type(value.__name__)))

    @staticmethod
    def tostring_modvalue(value):
        """
        Turn a  representation of a module into a string representation

        :param value: module representation (either str or tuple)
        :return: string representation
        """
        if isinstance(value, str):
            return value
        elif isinstance(value, tuple):
            return ''.join(value)
        else:
            raise exceptions.FastrTypeError('Invalid module value type ({})!'.format(type(value.__name__)))

    def _run_commands_string(self, value):
        """
        Run the commands returned by environmentmodules, and warn for
        non-default commands

        :param value: str of commands returned by environmentmodules
        """
        for command in value.splitlines():
            match1 = re.match(r'^os.environ\[(?P<sep1>[\'"])(\w+)(?P=sep1)\] = (?P<sep2>[\'"]).*(?P=sep2);?\s*$', command)
            if match1 is None:
                match2 = re.match(r'^del os.environ\[(?P<sep1>[\'"])(\w+)(?P=sep1)\];?\s*$', command)
                if match2 is None:
                    log.warning('WARNING: Evaluating unchecked code: {!r}'.format(command))
            # We know this is bad practice, but we trust the code from environmentmodules
            # pylint: disable=exec-used
            exec(command)

        # Make sure loaded module list is synced
        self._sync_loaded()

    @property
    def loaded_modules(self):
        """
        List of currently loaded modules
        """
        return [''.join(x) for x in self._loaded_modules]

    @property
    def avail_modules(self):
        """
        List of avaible modules
        """
        return self._avail_modules

    def avail(self, namestart=None):
        """
        Print available modules in same way as commandline version

        :param namestart: filter on modules that start with namestart
        """
        for module in self._avail_modules:
            default = module[-1]
            module = '/'.join(module[:-1])
            if namestart is None or module.startswith(namestart):
                if default:
                    log.info('{} (default)'.format(module))
                else:
                    log.info(module)

    def isloaded(self, module):
        """
        Check if a specific module is loaded

        :param module: module to check
        :return: flag indicating the module is loaded
        """
        module = self.totuple_modvalue(module)

        if module[1] is not None:
            # Check if a module which doesn't match perfectly is loaded (but which is a match)
            for loaded in self._loaded_modules:
                if loaded[0] == module[0] and loaded[1].startswith(module[1]):
                    return True
            return False
        else:
            for mod in self._loaded_modules:
                if module[0] == mod[0]:
                    return True
            return False

    def load(self, module):
        """
        Load specified module

        :param module: module to load
        """
        module = self.tostring_modvalue(module)
        if self.isloaded(module):
            log.warning('Module {} is already loaded, unloading first!'.format(module))
            self.unload(module)

        stdout, stderr = self._module('load', module)

        if len(stderr) != 0:
            log.error('Encountered error when loading module:\n{}'.format(stderr))
        else:
            self._run_commands_string(stdout)

    def unload(self, module):
        """
        Unload specified module

        :param module: module to unload
        """
        module = self.tostring_modvalue(module)

        if module in self._protected:
            log.debug('Module {} is protected, skipping unload!'.format(module))
            return

        if not self.isloaded(module):
            log.warning('Module {} is not loaded, cannot unload!'.format(module))

        stdout, stderr = self._module('unload', module)

        if len(stderr) != 0:
            log.error('Encountered error when unloading module:\n{}'.format(stderr))
        else:
            self._run_commands_string(stdout)

    def reload(self, module):
        """
        Reload specified module

        :param module: module to reload
        """
        module = self.tostring_modvalue(module)
        if not self.isloaded(module):
            log.warning(': Module {} is not loaded, cannot unload first!'.format(module))
        else:
            stdout, stderr = self._module('unload', module)
            if len(stderr) != 0:
                log.error('Encountered error when unloading module:\n{}'.format(stderr))
            else:
                self._run_commands_string(stdout)

        stdout, stderr = self._module('load', module)
        if len(stderr) != 0:
            log.error('Encountered error when loading module:\n{}'.format(stderr))
        else:
            self._run_commands_string(stdout)

    def swap(self, module1, module2):
        """
        Swap one module for another one

        :param module1: module to unload
        :param module2: module to load
        """
        self.unload(module1)
        self.load(module2)

    def clear(self):
        """
        Unload all modules (except the protected modules as they cannot be
        unloaded). This should result in a clean environment.
        """
        for module in self.loaded_modules:
            self.unload(module)
