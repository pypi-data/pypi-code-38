# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from polyaxon_nginx.schemas.base import get_config

OPTIONS = """
upstream polyaxon {{
  server unix:/polyaxon/web/polyaxon.sock;
}}

server {{
    include polyaxon/polyaxon.base.conf;
}}
"""


def get_main_config():
    return get_config(options=OPTIONS,
                      indent=0)
