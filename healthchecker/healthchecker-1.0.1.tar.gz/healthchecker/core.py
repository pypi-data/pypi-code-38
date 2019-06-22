"""Core functions for HealthChecker."""

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

import asyncio
import concurrent.futures
import logging
from functools import partial as functools_partial
from typing import Dict, Iterable, List, Optional, Tuple, Union

from .objects import ServiceStatus, ServiceStatusList
from .utils import http_request

logger = logging.getLogger(__name__)


def healthcheck_url(url: str, validation: Optional[str] = None,
                    *, timeout: Union[float, int], log: bool = False,
                    **kwargs) -> ServiceStatus:
    """Check if a URL is alive or not.

    Optionally, it checks for a string existing in the body. The OK attribute
    of the result is True if the request is OK and the string is found or False
    otherwise.

    Considers the timeout and warn if request takes longer than 60% of the time.

    It takes any other keyword parameter that the requests library accepts.

    :param url: URL to verify.
    :param timeout: How long to wait for a response.
    :param validation: [optional] String to find in the response body.
    :param log: [optional] True to enable logging, False to disable (default).

    :return: A ServiceStatus object with the requested URL, its status and
             checks results.
    """
    if log:
        logger.info('Begin checking URL %s...', url)

    response, request_time, error = http_request('GET', url, timeout=timeout,
                                                 log=log, **kwargs)
    body = '' if error else response.text
    # Accept HTTP 4xx as alive but not OK
    alive = not error and 200 <= response.status_code < 500
    ok = validation in body if validation and alive and response.ok \
        else alive and response.ok
    result = ServiceStatus(url, alive, ok)

    if log:
        if error and request_time > timeout:
            logger.warning('Request to %s timed out taking %.2f seconds', url,
                           request_time)
        elif log and request_time > (0.6 * timeout):
            logger.warning('Request to %s took too long: %.2f seconds', url,
                           request_time)
        logger.info('Finish checking URL: %s', str(result))

    return result


async def healthcheck_urls(urls: Iterable[str],
                           validations: Optional[Union[List[str], Tuple[str]]] = None,
                           *,
                           timeout: Union[float, int],
                           log: bool = False, **kwargs) -> ServiceStatusList:
    """Asynchronously check given URLs status, optionally validating them.

    It takes any other keyword parameter that the requests library accepts.

    :param urls: URLs to verify.
    :param timeout: How long to wait for a response for each URL.
    :param validations: [optional] A list of strings to find in the respective
                        response body. If there're more URLs than validation
                        strings, the last one is used for the remaining URLs.
    :param log: [optional] True to enable logging, False to disable (default).

    :return: A ServiceStatusList object with each requested URL, its status and
             checks results.
    """
    statuses = ServiceStatusList()
    with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
        loop = asyncio.get_event_loop()
        futures = []
        for index, url in enumerate(urls):
            if validations:
                try:
                    validation = validations[index]
                except IndexError:
                    validation = validations[-1]
            else:
                validation = None
            futures.append(
                loop.run_in_executor(
                    executor,
                    functools_partial(
                        healthcheck_url,
                        url,
                        validation,
                        timeout=timeout,
                        log=log,
                        **kwargs,
                    )
                )
            )
        for result in await asyncio.gather(*futures):
            statuses.append(result)
    return statuses


def notify(url: str, payload: Optional[str] = None,
           headers: Optional[Dict[str, str]] = None,
           *, log: bool = False, **kwargs) -> bool:
    """Execute a POST request as a notification with optional data.

    It takes any other keyword parameter that the requests library accepts.

    :param url: URL to POST notification.
    :param payload: [optional] Payload to POST (will be UTF-8 encoded).
    :param headers: [optional] Headers to send with the request.
    :param log: [optional] True to enable logging, False to disable (default).

    :return: True if the request was successful, False otherwise.
    """
    data = payload.encode('utf-8') if payload else None
    response, _, error = http_request('POST', url, timeout=5, log=log, data=data,
                                      headers=headers, **kwargs)
    return not error and response.ok
