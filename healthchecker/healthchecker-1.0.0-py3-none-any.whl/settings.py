"""Settings for HealthChecker."""

# -----------------------------------------------------------------------------
# Copyright (C) 2019 HacKan (https://hackan.net)
#
# This file is part of HealthChecker.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# -----------------------------------------------------------------------------

import logging.config
import os
from typing import List, Optional

_loglevel_raw = os.getenv('HEALTHCHECKER_LOG_LEVEL', 'INFO').upper()
LOGLEVEL: str = _loglevel_raw \
    if _loglevel_raw in ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL') \
    else 'INFO'
LOGGING: dict = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} p:{process:d} t:{thread:d} '
                      '[{name}.{funcName}:{lineno:d}] {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        # 'file': {
        #     'class': 'logging.FileHandler',
        #     'formatter': 'simple',
        #     'filename': 'healthchecker.log',
        # },
    },
    'loggers': {
        'healthchecker': {
            'handlers': ['console'],
            'level': LOGLEVEL,
        },
    },
}
logging.config.dictConfig(LOGGING)

# See https://github.com/settings/developers
GITHUB_API_TOKEN: str = os.getenv('HEALTHCHECKER_GITHUB_API_TOKEN')
GITHUB_REPO: str = os.getenv('HEALTHCHECKER_GITHUB_REPO')
GITHUB_FILENAME: str = os.getenv('HEALTHCHECKER_GITHUB_FILENAME')
GITHUB_BRANCH: str = os.getenv('HEALTHCHECKER_GITHUB_BRANCH', 'master')
GITHUB_COMMITTER_EMAIL: str = os.getenv('HEALTHCHECKER_GITHUB_COMMITTER_EMAIL',
                                        'hackan+healthchecker@rlab.be')

# Comma-separated URLs list
URLS: List[str] = os.getenv('HEALTHCHECKER_URLS', '').split(',')

# Comma-separated list of validations to run on given URLs
URLS_VALIDATION: List[str] = os.getenv('HEALTHCHECKER_URLS_VALIDATION', '').split(',')

# Requests timeout in seconds
REQUESTS_TIMEOUT: str = os.getenv('HEALTHCHECKER_REQUESTS_TIMEOUT', '10')

# URL to send failed checks via POST as notification
NOTIFY_URL: Optional[str] = os.getenv('HEALTHCHECKER_NOTIFY_URL')

# Optional payload to send to the notify URL
# It prepends this payload to the comma-separated list of URLs that failed
# validation, unless that it contains the string HEALTHCHECKER_FAILED_URLS
# (case sensitive), where it will replace that string by the comma-separated
# list of URLs, and send the entire payload.
# Example 1: HEALTHCHECKER_NOTIFY_PAYLOAD=here comes the failed urls...
# Example 2: HEALTHCHECKER_NOTIFY_PAYLOAD={"data": "HEALTHCHECKER_FAILED_URLS"}
NOTIFY_PAYLOAD: Optional[str] = os.getenv('HEALTHCHECKER_NOTIFY_PAYLOAD')

# Optional comma-separated list of headers to send to the notify URL
# The headers must be specified as name and value separated by a space:
# <header name> <header value>, and successive headers separated by comma.
# Example 1: HEALTHCHECKER_NOTIFY_HEADERS=X-Auth:4c18a291d7d8e7946cb9db9cbb3e1f49
# Example 2: HEALTHCHECKER_NOTIFY_HEADERS=Content-Type:application/json,X-MyVal:1
NOTIFY_HEADERS: List[str] = os.getenv('HEALTHCHECKER_NOTIFY_HEADERS', '').split(',')

# Use JSON to send the failed URLs
# This already sets a JSON header
_notify_json = os.getenv('HEALTHCHECKER_NOTIFY_JSON', 'false').lower()
NOTIFY_JSON: bool = True if _notify_json == 'true' else False

# Settings override
try:
    from .local_settings import *  # noqa
except ImportError:
    pass
