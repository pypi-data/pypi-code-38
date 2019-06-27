# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from polyaxon_nginx import settings
from polyaxon_nginx.schemas.buffering import get_buffering_config
from polyaxon_nginx.schemas.charset import get_charset_config
from polyaxon_nginx.schemas.error_page import get_error_page_config
from polyaxon_nginx.schemas.gzip import get_gzip_config
from polyaxon_nginx.schemas.listen import get_listen_config
from polyaxon_nginx.schemas.locations import get_locations_config
from polyaxon_nginx.schemas.logging import get_logging_config
from polyaxon_nginx.schemas.plugins import get_plugins_location_config
from polyaxon_nginx.schemas.ssl import get_ssl_config
from polyaxon_nginx.schemas.timeout import get_timeout_config
from polyaxon_nginx.schemas.uwsgi import get_uwsgi_config
from polyaxon_nginx.schemas.ws import get_ws_location_config


def get_polyaxon_config():
    config = [
        get_listen_config(),
    ]
    if settings.SSL_ENABLED:
        config.append(get_ssl_config())
    config += [
        get_logging_config(),
        get_gzip_config(),
        get_charset_config(),
        get_buffering_config(),
        get_timeout_config(),
        get_uwsgi_config(),
        get_error_page_config(),
        get_locations_config(),
        get_ws_location_config(),
    ]
    config += get_plugins_location_config()

    return '\n'.join(config)
