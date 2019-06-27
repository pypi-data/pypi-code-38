# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from polyaxon_nginx import settings
from polyaxon_nginx.schemas.base import get_config

STATIC_LOCATION_OPTIONS = """
location /static/ {{
    alias /polyaxon/static/;
    autoindex on;
    expires                   30d;
    add_header                Cache-Control private;
}}
"""


def get_static_location_config():
    return get_config(options=STATIC_LOCATION_OPTIONS,
                      indent=0)


TMP_LOCATION_OPTIONS = """
location /tmp/ {{
    alias                     /tmp/;
    expires                   0;
    add_header                Cache-Control private;
    internal;
}}
"""


def get_tmp_location_config():
    return get_config(options=TMP_LOCATION_OPTIONS,
                      indent=0)


REPOS_LOCATION_OPTIONS = """
location {repos_path}/ {{
    root                      {repos_path};
    expires                   0;
    add_header                Cache-Control private;
    internal;
}}
"""


def get_repos_location_config():
    return get_config(options=REPOS_LOCATION_OPTIONS,
                      indent=0,
                      repos_path=settings.REPOS_PATH)


DATA_LOCATION_OPTIONS = """
location {data_path}/ {{
    root                      {data_path};
    expires                   0;
    add_header                Cache-Control private;
    internal;
}}
"""


def get_data_location_config():
    return get_config(options=DATA_LOCATION_OPTIONS,
                      indent=0,
                      data_path=settings.DATA_PATH)


OUTPUTS_LOCATION_OPTIONS = """
location {outputs_path}/ {{
    root                      {outputs_path};
    expires                   0;
    add_header                Cache-Control private;
    internal;
}}
"""


def get_outputs_location_config():
    return get_config(options=OUTPUTS_LOCATION_OPTIONS,
                      indent=0,
                      outputs_path=settings.OUTPUTS_PATH)


def get_locations_config():
    config = [
        get_static_location_config(),
        get_tmp_location_config(),
        get_repos_location_config(),
        get_data_location_config(),
        get_outputs_location_config()
    ]
    return '\n'.join(config)
