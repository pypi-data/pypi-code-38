# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
"""Sanitizer used to remove sensitive data from our payload"""

import logging
import re

from . import config
from .utils import is_string, is_unicode

LOGGER = logging.getLogger(__name__)

MASK = '<Redacted by Sqreen>'

SENSITIVE_KEYS = [k.strip() for k in config.CONFIG["STRIP_SENSITIVE_KEYS"].split(',')]
LOGGER.debug("Using sensitive keys %s", ", ".join(SENSITIVE_KEYS))
try:
    SENSITIVE_REGEX = re.compile(config.CONFIG["STRIP_SENSITIVE_REGEX"])
except re.error:
    SENSITIVE_REGEX = re.compile(config.CONFIG_DEFAULT_VALUE["STRIP_SENSITIVE_REGEX"])
    LOGGER.warning("Invalid regexp configuration: %s", config.CONFIG["STRIP_SENSITIVE_REGEX"])
finally:
    LOGGER.debug("Using sensitive regex %s", SENSITIVE_REGEX.pattern)


def strip_sensitive_data(data, keys=SENSITIVE_KEYS, regex=SENSITIVE_REGEX):
    """Sanitize sensitive data from an object"""
    if is_string(data):
        if not is_unicode(data):
            data = data.decode("utf-8", errors="replace")

        if regex.match(data):
            return MASK
        return data

    if isinstance(data, dict):
        sanitize_data = {}
        for k, v in data.items():
            if k in keys:
                sanitize_data[k] = MASK
            else:
                sanitize_data[k] = strip_sensitive_data(v, keys, regex)

        return sanitize_data

    if isinstance(data, (list, tuple, set)):
        return [strip_sensitive_data(v, keys, regex) for v in data]

    return data
