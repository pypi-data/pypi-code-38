"""
Make yaml respect OrderedDicts and stop sorting things
"""
from collections import OrderedDict
import sys

import yaml


_items = 'viewitems' if sys.version_info < (3,) else 'items'


def map_representer(dumper, data):
    return dumper.represent_dict(getattr(data, _items)())


def map_constructor(loader, node): # pragma: nocover (python 3.6 doesn't use it)
    loader.flatten_mapping(node)
    return OrderedDict(loader.construct_pairs(node))


yaml.add_representer(dict, map_representer)
yaml.add_representer(OrderedDict, map_representer)

if sys.version_info < (3, 6): # pragma: nocover
    yaml.add_constructor('tag:yaml.org,2002:map', map_constructor)
