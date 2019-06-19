import logging

import typing
import attr
import cattr

import math
from functools import reduce


# create logger
module_logger = logging.getLogger(__name__)
module_logger.setLevel(logging.DEBUG)


def add_attr_description(attrib, description=None):
    attrib.metadata['__description'] = description
    return attrib

def get_attr_description(cls, attr_name):
    meta = attr.fields_dict(cls)[attr_name]
    return meta.metadata['__description']

