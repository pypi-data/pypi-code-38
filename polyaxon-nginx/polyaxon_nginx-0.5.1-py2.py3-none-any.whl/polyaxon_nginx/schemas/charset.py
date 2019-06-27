# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from polyaxon_nginx.schemas.base import get_config

OPTIONS = """
charset utf-8;
"""


def get_charset_config():
    return get_config(options=OPTIONS,
                      indent=0)
