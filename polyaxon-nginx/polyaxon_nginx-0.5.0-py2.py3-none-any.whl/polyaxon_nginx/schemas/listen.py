# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from polyaxon_nginx import settings
from polyaxon_nginx.schemas.base import get_config

HTTP_OPTIONS = """
listen 80;
"""

SSL_OPTIONS = """
listen 443 ssl;
ssl on;
"""


def get_listen_config():
    return get_config(options=SSL_OPTIONS if settings.SSL_ENABLED else HTTP_OPTIONS,
                      indent=0)
