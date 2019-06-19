# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from polyaxon_nginx import settings
from polyaxon_nginx.schemas.base import get_config

OPTIONS = """
send_timeout {timeout};
keepalive_timeout {timeout};
uwsgi_read_timeout {timeout};
uwsgi_send_timeout {timeout};
client_header_timeout {timeout};
proxy_read_timeout {timeout};
"""


def get_timeout_config():
    return get_config(options=OPTIONS,
                      indent=0,
                      timeout=settings.TIMEOUT)
