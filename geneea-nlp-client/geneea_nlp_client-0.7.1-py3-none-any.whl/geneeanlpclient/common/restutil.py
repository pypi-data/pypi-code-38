# Copyright 2019 Geneea Analytics s.r.o.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Functions related to calling REST APIs
"""

import json
import logging
import requests
from requests.auth import AuthBase
from typing import Any, Callable, Dict, Optional, TypeVar, Union


LOG = logging.getLogger(__name__)

DEFAULT_CONNECT_TIMEOUT = 3.05
DEFAULT_READ_TIMEOUT = 600

InputData = TypeVar('InputData')
OutputData = TypeVar('OutputData')


def remoteCall(url: str, *,
        method: str = 'POST',
        inputData: InputData = None,
        params: Dict[str, Any] = None,
        auth: Union[str, AuthBase] = None,
        serialize: Callable[[InputData], str] = json.dumps,
        deserialize: Callable[[str], OutputData] = json.loads,
        connectTimeout: float = DEFAULT_CONNECT_TIMEOUT,
        readTimeout: float = DEFAULT_READ_TIMEOUT,
        session: requests.Session = None,
        **kwargs
) -> Optional[OutputData]:
    """
    Call REST API on specified URL with specified parameters.

    :param url: URL to call
    :param method: http request method, 'POST' or 'GET'
    :param inputData: input data object
    :param params: http request parameter
    :param auth: http 'Authorization' header, has priority over 'key' if specified, or 'AuthBase' object
    :param serialize: function inputData -> str to be sent to server
    :param deserialize: function str -> output data object
    :param connectTimeout: connection timeout see: http://docs.python-requests.org/en/latest/user/advanced/#timeouts
    :param readTimeout: read timeout see: http://docs.python-requests.org/en/latest/user/advanced/#timeouts
    :param session: requests.Session object (useful for connection pooling)
    :return: deserialized API response or Exception in case of any error
    @throws: requests.RequestException
    """

    request = session.request if session else requests.request

    resp = request(method, url,
        auth=auth if isinstance(auth, AuthBase) else None,
        data=serialize(inputData) if inputData else None,
        params=params,
        timeout=(connectTimeout, readTimeout),
        **kwargs
    )
    resp.raise_for_status()
    resp.encoding = 'utf-8'
    return deserialize(resp.text) if resp.text else None

