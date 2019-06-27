# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from polyaxon_nginx.schemas.base import get_config

OPTIONS = """
gzip                        on;
gzip_disable                "msie6";
gzip_types                  *;
"""


def get_gzip_config():
    return get_config(options=OPTIONS,
                      indent=0)
