#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Author: zhangkai
Email: zhangkai@cmcm.com
Last modified: 2018-01-05 19:42:57
'''
import yaml

from .utils import DictUnwrapper
from .utils import DictWrapper

__all__ = ['load', 'dump']


def load(stream, **kwargs):
    doc = yaml.load(stream, **kwargs)
    return DictWrapper(doc)


def dump(doc, stream=None, default_flow_style=False, allow_unicode=True, **kwargs):
    doc = DictUnwrapper(doc)
    return yaml.dump(doc, stream=stream, default_flow_style=default_flow_style, allow_unicode=allow_unicode, **kwargs)
