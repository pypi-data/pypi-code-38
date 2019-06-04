# Copyright 2015 Oliver Cope
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
#
from __future__ import absolute_import

import imp
import sys
from random import randint
from time import time


class Options(dict):
    """\
    Options dictionary. An instance of this is attached to each
    :class:`fresco.core.FrescoApp` instance, as a central store for
    configuration options.
    """

    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, key, value):
        self[key] = value

    def update_from_file(self, path, load_all=False):
        """
        Update the instance with any symbols found in the python source file at
        `path`.

        :param path: The path to a python source file
        :param load_all: If true private symbols will also be loaded into the
                         options object.
        """
        module_name = 'fresco_options_%d%d' % (time(), randint(0, sys.maxsize))
        module = imp.load_source(module_name, path)
        self.update_from_object(module, load_all)
        del sys.modules[module_name]

    def update_from_object(self, ob, load_all=False):
        """
        Update the instance with any symbols listed in object `ob`
        :param load_all: If true private symbols will also be loaded into the
                         options object.
        """
        if load_all:
            symbols = dir(ob)
        else:
            symbols = getattr(ob, '__all__', None)
            if symbols is None:
                symbols = [name for name in dir(ob)
                                if not name.startswith('_')]
        self.update((s, getattr(ob, s)) for s in symbols)
