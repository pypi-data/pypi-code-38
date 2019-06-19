# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from polyaxon_nginx.schemas.base import get_config

UWSGI_OPTIONS = """
location / {{
    include     /etc/nginx/uwsgi_params;
    uwsgi_pass  polyaxon;
    uwsgi_param Host				$host;
    uwsgi_param X-Real-IP			$remote_addr;
    uwsgi_param X-Forwarded-For		$proxy_add_x_forwarded_for;
    uwsgi_param X-Forwarded-Proto	$http_x_forwarded_proto;
}}
"""


def get_uwsgi_config():
    return get_config(options=UWSGI_OPTIONS,
                      indent=0)
