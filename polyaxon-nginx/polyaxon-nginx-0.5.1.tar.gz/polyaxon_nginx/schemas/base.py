# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from polyaxon_nginx import settings


def _get_indent(indent):
    return settings.INDENT_CHAR * settings.INDENT_WIDTH * indent


def get_config(options, indent=0, **kwargs):
    _options = options.format(**kwargs)
    config = []
    for p in _options.split('\n'):
        config.append('{}{}'.format(_get_indent(indent), p))

    return '\n'.join(config)
