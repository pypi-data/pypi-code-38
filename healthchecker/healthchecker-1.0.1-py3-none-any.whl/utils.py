"""Helper functions definition."""

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

import logging
from time import time
from typing import Tuple, Union
from urllib.parse import urlparse

import requests

logger = logging.getLogger(__name__)


def parse_url(url: str) -> str:
    """URL parser to fix URLs with missing protocol.

    :param url: URL to parse.
    :return: Parsed URL with protocol set to http if missing.
    """
    url_raw = url.strip()
    parsed_url = urlparse(url_raw)
    if parsed_url.scheme not in ('http', 'https'):
        parsed_url = urlparse('http://' + url_raw)
    return parsed_url.geturl()


def http_request(method: str, url: str, *, timeout: Union[float, int],
                 log: bool = False, **kwargs) -> Tuple[requests.Response, float, bool]:
    """Execute a request to an URL and return the response.

    Additionally, return the request time and an error flag.

    :param method: Request method (GET, POST, PUT, ...).
    :param url: URL to request.
    :param timeout: How long to wait for a response.
    :param log: [optional] True to enable logging, False to disable (default).

    :return: A tuple with the response, the time it took and an error flag.
    """
    error = False
    response = requests.Response()
    request_time_start = time()
    try:
        response = requests.request(method, url, timeout=timeout, **kwargs)
        request_time_end = time()
    except (requests.exceptions.ConnectionError,
            requests.exceptions.ReadTimeout,
            requests.exceptions.InvalidURL,
            requests.exceptions.InvalidSchema) as e:
        request_time_end = time()
        if log:
            logger.error('Error %sing data from/to %s: %s', method, url, repr(e))
        error = True
    else:
        if log and not response.ok:
            logger.warning(
                'Response from %s is NOT OK: %d %s',
                url,
                response.status_code,
                response.text
            )
    request_time = request_time_end - request_time_start
    if log:
        logger.debug('Request to %s took %.2f seconds', url, request_time)
    return response, request_time, error
