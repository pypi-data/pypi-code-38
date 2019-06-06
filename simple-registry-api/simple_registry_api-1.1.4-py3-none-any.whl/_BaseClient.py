"""
    Copyright 2019 sbienkow
    Copyright 2015 Yodle, Inc.

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
import logging
import json
from collections import namedtuple

from requests import Session
from requests.exceptions import HTTPError
from .AuthorizationService import AuthorizationService

logger = logging.getLogger(__name__)


class CommonBaseClient(object):
    def __init__(self, host, verify_ssl=None, username=None, password=None,
                 api_timeout=None):
        self.host = host

        self._session = session = Session()
        self._get = session.get
        self._put = session.put
        self._delete = session.delete

        self.method_kwargs = {}
        if verify_ssl is not None:
            self.method_kwargs['verify'] = verify_ssl
        if username is not None and password is not None:
            session.auth = (username, password)
        if api_timeout is not None:
            self.method_kwargs['timeout'] = api_timeout

    def _http_response(self, url, method, data=None, **kwargs):
        """url -> full target url
           method -> method from requests
           data -> request body
           kwargs -> url formatting args
        """
        header = {'content-type': 'application/json'}

        if data:
            data = json.dumps(data)
        path = url.format(**kwargs)
        logger.debug("%s %s", method.__name__.upper(), path)
        try:
            response = method(self.host + path,
                              data=data, headers=header, **self.method_kwargs)
            logger.debug("%s %s", response.status_code, response.reason)
            response.raise_for_status()
        except Exception:
            self._session.close()
            raise

        return response

    def _http_call(self, url, method, data=None, **kwargs):
        """url -> full target url
           method -> method from requests
           data -> request body
           kwargs -> url formatting args
        """
        response = self._http_response(url, method, data=data, **kwargs)
        if not response.content:
            return {}

        return response.json()


class BaseClientV2(CommonBaseClient):
    _Manifest = namedtuple('_Manifest', 'content, type, digest')
    BASE_CONTENT_TYPE = 'application/vnd.docker.distribution.manifest'
    LIST_TAGS = '/v2/{name}/tags/list'
    MANIFEST = '/v2/{name}/manifests/{reference}'
    BLOB = '/v2/{name}/blobs/{digest}'
    schema_1_signed = BASE_CONTENT_TYPE + '.v1+prettyjws'
    schema_1 = BASE_CONTENT_TYPE + '.v1+json'
    schema_2 = BASE_CONTENT_TYPE + '.v2+json'
    schema_blob = 'application/vnd.docker.container.image.v1+json'

    def __init__(self, *args, **kwargs):
        auth_service_url = kwargs.pop("auth_service_url", "")
        super(BaseClientV2, self).__init__(*args, **kwargs)
        self.auth = AuthorizationService(
            registry=self.host,
            url=auth_service_url,
            verify=self.method_kwargs.get('verify', False),
            auth=self.method_kwargs.get('auth', None),
            api_timeout=self.method_kwargs.get('api_timeout')
        )

    @property
    def version(self):
        return 2

    def check_status(self):
        self.auth.desired_scope = 'registry:catalog:*'
        return self._http_call('/v2/', self._get)

    def catalog(self):
        self.auth.desired_scope = 'registry:catalog:*'
        return self._http_call('/v2/_catalog', self._get)

    def get_repository_tags(self, name):
        self.auth.desired_scope = 'repository:%s:*' % name
        return self._http_call(self.LIST_TAGS, self._get, name=name)

    def get_manifest_and_digest(self, name, reference):
        m = self.get_manifest(name, reference)
        return m.content, m.digest

    def get_manifest(self, name, reference):
        self.auth.desired_scope = 'repository:%s:*' % name
        response = self._http_response(
            self.MANIFEST, self._get, name=name, reference=reference,
            schema=self.schema_2,
        )
        return self._Manifest(
            content=response.json(),
            type=response.headers.get('Content-Type', 'application/json'),
            digest=response.headers.get('Docker-Content-Digest'),
        )

    def delete_manifest(self, name, digest):
        self.auth.desired_scope = 'repository:%s:*' % name
        return self._http_call(self.MANIFEST, self._delete,
                               name=name, reference=digest)

    def get_blob(self, name, digest, schema=schema_blob):
        self.auth.desired_scope = 'repository:%s:*' % name
        response = self._http_response(
            self.BLOB, self._get, name=name, digest=digest,
            schema=schema,
        )
        return response.json()

    def delete_blob(self, name, digest):
        self.auth.desired_scope = 'repository:%s:*' % name
        return self._http_call(self.BLOB, self._delete,
                               name=name, digest=digest)

    def _http_response(self, url, method, data=None, content_type=None,
                       schema=None, **kwargs):
        """url -> full target url
           method -> method from requests
           data -> request body
           kwargs -> url formatting args
        """

        if schema is None:
            schema = self.schema_2

        header = {
            'content-type': content_type or 'application/json',
            'Accept': schema,
        }

        # Token specific part. We add the token in the header if necessary
        auth = self.auth
        token_required = auth.token_required
        token = auth.token
        desired_scope = auth.desired_scope
        scope = auth.scope

        if token_required:
            if not token or desired_scope != scope:
                logger.debug("Getting new token for scope: %s", desired_scope)
                auth.get_new_token()

            header['Authorization'] = 'Bearer %s' % self.auth.token

        if data and not content_type:
            data = json.dumps(data)

        path = url.format(**kwargs)
        logger.debug("%s %s", method.__name__.upper(), path)
        response = method(self.host + path,
                          data=data, headers=header, **self.method_kwargs)
        logger.debug("%s %s", response.status_code, response.reason)
        response.raise_for_status()

        return response


def BaseClient(host, verify_ssl=None, api_version=None, username=None,
               password=None, auth_service_url="", api_timeout=None):
    if api_version == 1:
        raise NotImplementedError
    elif api_version == 2:
        return BaseClientV2(
            host, verify_ssl=verify_ssl, username=username, password=password,
            auth_service_url=auth_service_url, api_timeout=api_timeout,
        )
    elif api_version is None:
        # Try V2 first
        logger.debug("checking for v2 API")
        v2_client = BaseClientV2(
            host, verify_ssl=verify_ssl, username=username, password=password,
            auth_service_url=auth_service_url, api_timeout=api_timeout,
        )
        try:
            v2_client.check_status()
        except HTTPError as e:
            if e.response.status_code == 404:
                raise NotImplementedError
        else:
            logger.debug("using v2 API")
            return v2_client
    else:
        raise RuntimeError('invalid api_version')
