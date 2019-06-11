import requests

from urllib.parse import urlparse, urljoin
from dli import __version__
import json as json_lib
import time

from dli.client.exceptions import (
    InvalidPayloadException,
    UnAuthorisedAccessException,
    InsufficientPrivilegesException,
    DatalakeException
)

# Python 2.7 / 3.x differences
try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError


def make_hook(root, get_header):
    def _make_empty_response(r):
        import copy
        response = copy.deepcopy(r)
        response._content = b'{"class": ["none"]}'
        return response

    def _extract_error_response_message(r):
        try:
            return r.json()['errorText']
        except (JSONDecodeError, KeyError):
            return r.text

    def _response_hook(r, *args, **kwargs):

        if r.status_code in [201, 202, 204, 404]:  # for now. or (300 <= r.status_code <= 399):
            return _make_empty_response(r)
        elif r.status_code in [400, 422]:
            raise InvalidPayloadException(_extract_error_response_message(r))
        elif r.status_code == 401:
            raise UnAuthorisedAccessException(_extract_error_response_message(r))
        elif r.status_code == 403:
            raise InsufficientPrivilegesException(_extract_error_response_message(r))
        elif r.status_code > 400:
            raise DatalakeException(_extract_error_response_message(r))
    return _response_hook


class DliRequestFactoryFactory(object):
    def __init__(self, root, host=None, auth_header=lambda: {}):
        self.root = root
        self.host = host
        self.auth_header = auth_header

    def request_factory(self, method=None, url=None, headers=None, files=None, data=None,
                        params=None, auth=None, cookies=None, hooks=None, json=None):

        # relative uri? make it absolute.
        if not urlparse(url).netloc:
            url = urljoin(str(self.root), str(url))     # python 2/3 nonsense

        # uri template substitution.
        pars = params if method == "GET" else data

        if pars:
            if '__json' in pars:
                js = json_lib.loads(pars['__json'])
                pars.update(js)
                del pars['__json']

        if pars and method == "GET":
            params = pars
        else:
            json = pars
            data = None

        # populate headers
        if not headers:
            headers = {}
        headers['Content-Type'] = "application/vnd.siren+json"
        headers["X-Data-Lake-SDK-Version"] = str(__version__)
        headers.update(self.auth_header())

        # if a host has been provided, then we need to set it on the header
        if self.host:
            headers['Host'] = self.host

        if not hooks:
            hooks = {}
        if 'response' not in hooks:
            hooks['response'] = []
        hooks['response'] = make_hook(self.root, self.auth_header)

        return requests.Request(
            method=method,
            url=url,
            headers=headers,
            files=files,
            data=data,
            params=params,
            auth=auth,
            cookies=cookies,
            hooks=hooks,
            json=json
        )
