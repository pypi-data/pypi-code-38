# Copyright (c) 2015, Combine Control Systems AB
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Combine Control Systems AB nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.
# IN NO EVENT SHALL COMBINE CONTROL SYSTEMS AB BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import pkgutil
import importlib
import six

from .backends import layers
from .backends import systems


LAYER_MOD_PATH = 'backends.layers'
BACKEND_MOD_PATH = 'backends.systems'


class LazyModuleDict(dict):
    """Import modules lazy on access."""

    def __init__(self, module):
        super(LazyModuleDict, self).__init__()
        self.path = module.__path__
        for importer, modname, ispkg in pkgutil.iter_modules(module.__path__):
            self[modname] = importer.find_module(modname)

    @staticmethod
    def __import_children(item, full_modname, path):
        for importer, modname, ispkg in pkgutil.iter_modules(
                path):
            # TODO(stefan): Import backend modules lazily to avoid multiple
            #               backend imports.
            # Note: Importing using this method requires unique namespaces
            #       for each module, otherwise already existing modules
            #       are overwritten since a module reload is performed on
            #       the existing module already in the self dictionary on
            #       another item. This is why full_modname is important.
            full_modname = '{}.{}'.format(full_modname, modname)
            module = (
                importer.find_module(full_modname).load_module(full_modname))
            item.__dict__[modname] = module

    def __getitem__(self, modname):
        item = super(LazyModuleDict, self).__getitem__(modname)
        if isinstance(item, pkgutil.ImpLoader):
            full_modname = '{}.{}'.format(LAYER_MOD_PATH, modname)
            item = item.load_module(full_modname)
            self.__import_children(item, full_modname, item.__path__)
            super(LazyModuleDict, self).__setitem__(modname, item)
        elif six.PY3 and isinstance(
                item, importlib.machinery.SourceFileLoader):
            lm = item.load_module(modname)
            full_modname = '{}.{}'.format(LAYER_MOD_PATH, modname)
            self.__import_children(item, full_modname, lm.__path__)
        return item


def get_layer_module(layer_name):
    return layer_modules[layer_name]


def get_layer_meta(layer_name):
    return get_layer_module(layer_name).layer.Layer.meta


def get_backend(backend_name):
    return backend_modules[backend_name].backend


layer_modules = LazyModuleDict(layers)
backend_modules = LazyModuleDict(systems)

available_plugins = {
    'layers': sorted(layer_modules.keys()),
    'systems': sorted(backend_modules.keys())
}
