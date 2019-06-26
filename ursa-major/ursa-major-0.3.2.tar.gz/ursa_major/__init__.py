# -*- coding: utf-8 -*-
# Copyright (c) 2018  Red Hat, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Written by Chenxiong Qi <cqi@redhat.com>

# Copied from MBS code
MBS_BUILD_STATES = {
    "init": 0,
    "wait": 1,
    "build": 2,
    "done": 3,
    "failed": 4,
    "ready": 5,
    "garbage": 6,
}


class ModuleConfigCmp(object):
    # User input module was not added to configuration file yet.
    NEW = 0
    # User input module has same config with the one in configuration file.
    # That means name is same, stream is same, and requires is also the
    # same.
    SAME = 1
    # User input module has different config from the one found in
    # configuration file.
    # Probably either stream or requires is different, or both
    DIFFERENT = 2


class ModuleConfig(object):
    """Class representing a module config"""

    def __init__(self, module_config):
        self._raw_module_config = module_config
        self.priority = module_config.get('priority')
        self.name = module_config['name']
        self.stream = module_config['stream']
        self.requires = module_config.get('requires', None)
        self.buildrequires = module_config.get('buildrequires', None)

    @property
    def raw_module_config(self):
        return self._raw_module_config

    def __str__(self):
        return '{}:{}:{!r}:{!r}'.format(
            self.name, self.stream, self.requires, self.buildrequires)

    def compare(self, other):
        """
        Compare user input module config with the one found from configuration
        file.
        """
        if other is None:
            return ModuleConfigCmp.NEW
        if self.priority != other.priority:
            return ModuleConfigCmp.DIFFERENT
        if self.requires != other.requires:
            return ModuleConfigCmp.DIFFERENT
        if self.buildrequires != other.buildrequires:
            return ModuleConfigCmp.DIFFERENT
        return ModuleConfigCmp.SAME
