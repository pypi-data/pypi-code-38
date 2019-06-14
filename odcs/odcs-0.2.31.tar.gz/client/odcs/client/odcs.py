# -*- coding: utf-8 -*-
# Copyright (c) 2017  Red Hat, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Written by Chenxiong Qi <cqi@redhat.com>

import json
import requests
import time

from six.moves import urllib_parse
from requests_kerberos import HTTPKerberosAuth


class AuthMech(object):
    OpenIDC = 1
    Kerberos = 2
    Anonymous = 3
    SSL = 4

    @classmethod
    def has(cls, mech):
        return mech in (cls.OpenIDC, cls.Kerberos, cls.Anonymous, cls.SSL)


def validate_int(value, min=1, type_error=None, value_error=None):
    if not isinstance(value, int):
        if type_error:
            raise TypeError(type_error)
        else:
            raise TypeError('Value {0} is not an integer.'.format(value))
    if value < min:
        if value_error:
            raise ValueError(value_error)
        else:
            raise ValueError(
                'Value {0} is less than minimal value {1}.'.format(
                    value, min))


def validate_page(value):
    validate_int(
        value,
        type_error='page number must be an integer.',
        value_error='page number must start from 1.')


def validate_per_page(value):
    validate_int(
        value,
        type_error='per_page must be an integer.',
        value_error='per_page must be greater than or equal to 1.')


class ODCS(object):
    """Client API to interact with ODCS APIs"""

    def __init__(self, server_url, api_version='1', verify_ssl=True,
                 auth_mech=None, openidc_token=None, ssl_cert=None,
                 ssl_key=None):
        """Initialize ODCS client

        :param str server_url: server URL of ODCS.
        :param str api_version: API version client will call. Version 1 is the default.
        :param bool verify_ssl: whether to verify SSL certificate over HTTP. By
            default, always verify, but you are also always able to disable it
            by passing False.
        :param AuthMech auth_mech: specify what authentication mechanism is
            used to interact with ODCS server. Choose one mechanism from
            AuthMech. Anonymous can be passed to force client not send
            any authentication information. If this parameter is omitted,
            same as Anonymous.
        :param str openidc_token: token got from OpenIDC so that client can be
            authenticated by ODCS server. This is only required if
            ``AuthMech.OpenIDC`` is passed to parameter ``auth_mech``.
        :param str ssl_cert: Path to SSL client certificate to use. This is
            only required if ``AuthMech.SSL`` is passed to parameter
            ``auth_mech``.
        :param str ssl_key: Path to SSL client key to use. This is
            only required if ``AuthMech.SSL`` is passed to parameter
            ``auth_mech``.
        """
        self._server_url = server_url
        self._api_version = api_version
        self._verify_ssl = verify_ssl
        if auth_mech == AuthMech.OpenIDC and not openidc_token:
            raise ValueError('OpenIDC token must be specified when OpenIDC'
                             ' authentication is enabled.')
        self._openidc_token = openidc_token

        if auth_mech == AuthMech.SSL and (not ssl_cert or not ssl_key):
            raise ValueError('SSL cert and keymust be specified when SSL'
                             ' authentication is enabled.')
        self._ssl_cert = ssl_cert
        self._ssl_key = ssl_key

        if auth_mech is None:
            self._auth_mech = AuthMech.Anonymous
        else:
            if not AuthMech.has(auth_mech):
                raise ValueError(
                    'Unknown authentication mechanism {0}'.format(auth_mech))
            self._auth_mech = auth_mech

    @property
    def server_url(self):
        return self._server_url

    @property
    def api_version(self):
        return self._api_version

    @property
    def auth_mech(self):
        return self._auth_mech

    def _make_endpoint(self, resource_path):
        """Helper method to construct URL to requested resource

        URL of requested resource consists of the server URL, API version and
        the resource path.

        :param str resource_path: the part after API version representing
            the concrete resource.
        :return: the whole complete URL of requested resource.
        :rtype: str
        """
        return urllib_parse.urljoin(
            self._server_url,
            'api/{0}/{1}'.format(self.api_version, resource_path.lstrip('/')))

    def _make_request(self, method, resource_path, data=None):
        """Make a HTTP request to server

        :param str method: HTTP request method to send, GET, POST and DELETE
            are supported.
        :param str resource_path: path of requested resource.
        :param dict data: corresponding data with specific request. It is
            optional. None is default that means no data is send along with
            request.
        :return: requests Response object.
        :rtype: requests.Response
        :raises: if ODCS does not response 200 or 202, exception will be raised
            by ``requests.Response.raise_for_status``.
        """
        request_data = {}
        headers = {}
        if data:
            if method in ('post', 'patch'):
                request_data['data'] = json.dumps(data)
                headers['Content-Type'] = 'application/json'
            if method == 'get':
                request_data['params'] = data
        if not self._verify_ssl:
            request_data['verify'] = False
        if self.auth_mech == AuthMech.OpenIDC:
            headers['Authorization'] = 'Bearer {0}'.format(self._openidc_token)
        elif self.auth_mech == AuthMech.Kerberos:
            request_data['auth'] = HTTPKerberosAuth()
        elif self.auth_mech == AuthMech.SSL:
            request_data['cert'] = (self._ssl_cert, self._ssl_key)

        # Anonymous is the last possible value and no auth should be set

        if headers:
            request_data['headers'] = headers

        request_method = getattr(requests, method)
        resource_url = self._make_endpoint(resource_path)
        r = request_method(resource_url, **request_data)

        # Print error, for debugging
        if r.status_code not in (200, 202):
            print(r.text)

        r.raise_for_status()
        return r

    def _get(self, resource_path, data=None):
        """Make a GET HTTP request to server"""
        return self._make_request('get', resource_path, data)

    def _post(self, resource_path, data=None):
        """Make a POST HTTP request to server"""
        return self._make_request('post', resource_path, data)

    def _delete(self, resource_path, data=None):
        """Make a DELETE HTTP request to server"""
        return self._make_request('delete', resource_path, data)

    def _patch(self, resource_path, data=None):
        """Make a PATCH HTTP request to server"""
        return self._make_request('patch', resource_path, data)

    def new_compose(self, source, source_type,
                    seconds_to_live=None, packages=[], flags=[],
                    sigkeys=None, results=None, arches=None,
                    builds=None, modular_koji_tags=None,
                    module_defaults_url=None, module_defaults_commit=None,
                    lookaside_repos=None):
        """Request a new compose

        :param str source: from where to grab and make new compose, different
            value for different ``source_type``. For ``tag`` source type, name
            of the tag. For ``module`` source type, white-space separated list
            of module name-stream or name-stream-version. For ``repo`` source
            type, full path to repository.
        :param str source_type: source type. ``tag`` for compose from Koji tag,
            ``module`` for compose from the Fedora module, ``repo`` for compose
            from local RPM repository.
        :param int seconds_to_live: Number of seconds for which the compose
            should become available.
        :param list packages: List of packages to include in a compose. Must not
            be set for "module" source_type.
        :param list flags: List of flags influencing the resulting compose.
            Valid flags are 1) ``no_deps``, the resulting compose will contain
            only packages defined in the "packages" list without their
            dependencies, or for ``source_type`` of "module", only the modules
            listed in ``source`` without their dependencies.
        :param list sigkeys: List of signature keys by which the packages
            in compose must be signed.
        :param list results: List of additional results which will be generated
            by ODCS as part of this compose. Can be "iso" for iso files with
            packages or "boot.iso" for images/boot.iso needed to generate
            container base images or installable DVDs.
        :return: the newly created Compose
        :rtype: dict
        """
        request_data = {
            'source': {'source': source, 'type': source_type}
        }
        if packages:
            request_data['source']['packages'] = packages
        if builds:
            request_data['source']['builds'] = builds
        if sigkeys:
            request_data['source']['sigkeys'] = sigkeys
        if modular_koji_tags:
            request_data['source']['modular_koji_tags'] = modular_koji_tags
        if module_defaults_url:
            request_data['source']['module_defaults_url'] = module_defaults_url
        if module_defaults_commit:
            request_data['source']['module_defaults_commit'] = module_defaults_commit
        if lookaside_repos:
            request_data['lookaside_repos'] = lookaside_repos
        if seconds_to_live is not None:
            request_data['seconds-to-live'] = seconds_to_live
        if flags:
            request_data['flags'] = flags
        if results:
            request_data['results'] = results
        if arches:
            request_data['arches'] = arches

        r = self._post('composes/', request_data)
        return r.json()

    def renew_compose(self, compose_id, seconds_to_live=None):
        """To regenerate an expired compose

        :param int compose_id: Compose ID to renew.
        :param int seconds_to_live: Number of seconds for which the compose
            should become available.
        :return: the new regenerated Compose
        :rtype: dict
        """
        if seconds_to_live is not None:
            request_data = {'seconds-to-live': seconds_to_live}
        else:
            request_data = None

        r = self._patch('composes/{0}'.format(compose_id), request_data)
        return r.json()

    def find_composes(self, **search_criteria):
        """Find composes

        :param dict search_criteria: a mapping containing compose search
            criteria and pagination arguments. Composes can be searched
            by ``owner``, ``source_type``, ``source`` and ``state``.
        :return: list of found composes, each of them is a dict.
        :rtype: list
        """
        if 'page' in search_criteria:
            validate_page(search_criteria['page'])
        if 'per_page' in search_criteria:
            validate_per_page(search_criteria['per_page'])

        r = self._get('composes/', search_criteria)
        return r.json()

    def delete_compose(self, compose_id):
        """Delete a compose

        :param int compose_id: compose ID.
        :return: a mapping representing the acknowledge of a compose is delete.
        :rtype: dict
        """
        r = self._delete('composes/{0}'.format(compose_id))
        return r.json()

    def get_compose(self, compose_id):
        """Get a compose

        :param int compose_id: compose ID.
        :return: a mapping representing a compose.
        :rtype: dict
        """
        r = self._get('composes/{0}'.format(compose_id))
        return r.json()

    def wait_for_compose(self, compose_id, timeout=300):
        """
        Polls the ODCS server repeatedly to find out whether the compose
        moved from "wait" or "generating" state to some final state. Blocks
        for `timeout` seconds. If the compose does not move to the final state
        in given time limit, raises RuntimeError.

        NOTE: It is advised to use this method only in situations where the
        caller is not able to listen on fedmsg bus or UMB bus for the
        odcs.state.change messages which can inform the caller about the
        compose state change without the polling.

        :param int compose_id: compose ID.
        :param int timeout: Number of seconds to wait/block.
        :rtype: dict
        :return: a mapping representing a compose
        """
        elapsed = 0
        sleep_time = 1
        start_time = time.time()
        while True:
            compose = self.get_compose(compose_id)
            if compose['state_name'] not in ['wait', 'generating']:
                return compose

            elapsed = time.time() - start_time
            if elapsed >= timeout:
                raise RuntimeError(
                    "Retrieving ODCS compose %s timed out after %s seconds" %
                    (compose_id, timeout))

            time.sleep(sleep_time)

            # Increase the sleep time for next try. But do not try sleeping
            # longer than the `timeout`.
            elapsed = time.time() - start_time
            sleep_time = round(sleep_time * 1.5)
            if elapsed + sleep_time > timeout:
                sleep_time = timeout - elapsed
