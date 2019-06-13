"""
Copyright 2018 Cognitive Scale, Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import json
from typing import Dict, TypeVar, Type, Optional

import requests

from cortex_client.utils import get_cortex_profile
from .serviceconnector import ServiceConnector
from .types import InputMessage, JSONType
from .utils import get_logger

log = get_logger(__name__)

T = TypeVar('T', bound="_Client")


class _Client:
    """
    A client.
    """

    URIs = {} # type: Dict[str, str]

    def __init__(self, url, version, token, **kwargs):
        self._serviceconnector = ServiceConnector(url, version, token)

    def _post_json(self, uri, obj: JSONType):
        body_s = json.dumps(obj)
        headers = {'Content-Type': 'application/json'}
        r = self._serviceconnector.request('POST', uri, body_s, headers)
        if r.status_code not in [requests.codes.ok, requests.codes.created]:
            log.info("Status: {}, Message: {}".format(r.status_code, r.text))
        r.raise_for_status()
        return r.json()

    def _get(self, uri, debug=False, **kwargs):
        return self._serviceconnector.request('GET', uri, debug=debug, **kwargs)

    def _delete(self, uri, debug=False):
        r = self._serviceconnector.request('DELETE', uri, debug=debug)
        return r

    def _get_json(self, uri, debug=False) -> Optional[dict]:
        r = self._serviceconnector.request('GET', uri, debug=debug)
        # If the resource is not found, return None ...
        if r.status_code == requests.codes.not_found:
            return None
        r.raise_for_status()
        return r.json()

    def _request_json(self, uri, method='GET'):
        r = self._serviceconnector.request(method, uri)
        r.raise_for_status()
        return r.json()

    @classmethod
    def from_current_cli_profile(cls: Type[T], version:str="3", **kwargs) -> T:
        cli_cfg = get_cortex_profile()
        url, token = cli_cfg["url"], cli_cfg["token"]
        return cls(url, version, token, **kwargs)   # type: ignore # ignore until mypy properyly supports attr ...

    @classmethod
    def from_cortex_message(cls, message, version:str="3", **kwargs):
        return cls(message["apiEndpoint"], version, message["token"], **kwargs)


def build_client(type, input_message: InputMessage, version):
    """
    Builds a client.
    """
    return type(input_message.api_endpoint, version, input_message.token)
