"""
  Copyright (c) 2017-2019 Atrio, Inc.

  All rights reserved.
"""

import os
import sys

import ruamel.yaml as yaml

from alfredo import descriptions
from alfredo.resource import HttpPropertyResource

__version__ = '0.0.5'

DEFAULT_RUOTE_ROOT = 'https://apidemo.atrio.network'
DEFAULT_VIRGO_ROOT = 'https://virgo.atrio.network'


def represent_unicode(self, data):
    return self.represent_str(data.encode('utf-8'))


if sys.version_info < (3,):
    yaml.representer.Representer.add_representer(unicode, represent_unicode)


def ruote(token=None):
    ruote_root = os.getenv('RUOTE_ROOT', DEFAULT_RUOTE_ROOT)
    root = HttpPropertyResource(None, ruote_root, descriptions.ruote)
    if token is not None:
        root.headers = dict(Authorization="Token %s" % token)
    return root


def virgo():
    virgo_root = os.getenv('VIRGO_ROOT', DEFAULT_VIRGO_ROOT)
    return HttpPropertyResource(None, virgo_root, descriptions.virgo)
