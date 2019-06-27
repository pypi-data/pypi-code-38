# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from polyaxon_nginx import settings
from polyaxon_nginx.schemas.base import get_config

SSL_REDIRECT_OPTIONS = """
server {{
    listen 80;
    return 301 https://$host$request_uri;
}}
"""


def get_redirect_config():
    return get_config(options=SSL_REDIRECT_OPTIONS if settings.SSL_ENABLED else '',
                      indent=0,
                      ssl_path=settings.SSL_PATH)
