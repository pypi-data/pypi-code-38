# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from polyaxon_nginx import settings
from polyaxon_nginx.schemas.base import get_config

OPTIONS = """
error_log /polyaxon/logs/error.log {level};
"""


def get_logging_config():
    return get_config(options=OPTIONS,
                      indent=0,
                      level=settings.LOGGING_LEVEL)
