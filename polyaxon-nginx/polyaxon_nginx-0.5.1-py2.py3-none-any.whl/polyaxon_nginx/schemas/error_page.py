# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from polyaxon_nginx.schemas.base import get_config

OPTIONS = """
error_page 500 502 503 504 /50x.html;
"""


def get_error_page_config():
    return get_config(options=OPTIONS,
                      indent=0)
