""" Package utils"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import importlib
import pkgutil


def import_module(package, module):
    return importlib.import_module('{}.{}'.format(package, module))


def list_modules(package):
    return [name for _, name, ispkg in pkgutil.iter_modules([package]) if not ispkg]
