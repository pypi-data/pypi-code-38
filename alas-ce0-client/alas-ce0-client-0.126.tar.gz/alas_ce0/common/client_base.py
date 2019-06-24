import base64
import contextlib
import httplib
import os
import ssl
import urlparse
import json

from httplib2 import socks, AllHosts, ProxyInfo

import sys
reload(sys)
sys.setdefaultencoding('utf8')

URL_FETCH_DEADLINE = 300


def proxy_info_from_environment(method='http'):
    if method not in ['http', 'https']:
        return

    env_var = method + '_proxy'
    url = os.environ.get(env_var, os.environ.get(env_var.upper()))

    if not url:
        return

    pi = proxy_info_from_url(url, method)

    no_proxy = os.environ.get('no_proxy', os.environ.get('NO_PROXY', ''))
    bypass_hosts = []
    if no_proxy:
        bypass_hosts = no_proxy.split(',')
    # special case, no_proxy=* means all hosts bypassed
    if no_proxy == '*':
        bypass_hosts = AllHosts

    pi.bypass_hosts = bypass_hosts
    return pi


def proxy_info_from_url(url, method='http'):
    url = urlparse.urlparse(url)
    username = None
    password = None
    port = None
    if '@' in url[1]:
        ident, host_port = url[1].split('@', 1)
        if ':' in ident:
            username, password = ident.split(':', 1)
        else:
            password = ident
    else:
        host_port = url[1]
    if ':' in host_port:
        host, port = host_port.split(':', 1)
    else:
        host = host_port

    if port:
        port = int(port)
    else:
        port = dict(https=443, http=80)[method]

    proxy_type = socks.PROXY_TYPE_HTTP_NO_TUNNEL
    return ProxyInfo(
        proxy_type=proxy_type,
        proxy_host=host,
        proxy_port=port,
        proxy_user=username or None,
        proxy_pass=password or None
    )


class ApiClientBase(object):
    def __init__(self, **kwargs):
        self.for_app_engine = kwargs['for_app_engine'] if 'for_app_engine' in kwargs else True
        self.base_url = ''
        self.headers = {}

        if not kwargs:
            raise Exception('Must specify arguments.')

        self.base_url = kwargs['base_url']
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json; charset=UTF-8'
        }

        _url_parsed = urlparse.urlparse(self.base_url)
        self.host = _url_parsed.hostname
        self.port = _url_parsed.port
        self.scheme = _url_parsed.scheme

        self.username = kwargs['user_name']
        self.password = kwargs['password']
        if self.username and self.password:
            self.headers['Authorization'] = \
                'Basic ' + base64.encodestring(self.username + ':' + self.password).replace(os.linesep, '')

        self.args = kwargs
        self.timeout = 60
        self.source_address = kwargs['source_address'] if 'source_address' in kwargs else None

    @contextlib.contextmanager
    def _get_client(self):
        pi = proxy_info_from_environment()
        if pi:
            if self.scheme == 'http':
                yield httplib.HTTPConnection(
                    pi.proxy_host,
                    pi.proxy_port,
                    timeout=self.timeout,
                    source_address=self.source_address
                )
            else:
                yield httplib.HTTPSConnection(
                    pi.proxy_host,
                    pi.proxy_port,
                    timeout=self.timeout,
                    context=ssl._create_unverified_context(),
                    source_address=self.source_address
                )
        else:
            self.base_url = ''
            if self.scheme == 'http':
                yield httplib.HTTPConnection(
                    self.host,
                    self.port,
                    source_address=self.source_address
                )
            else:
                yield httplib.HTTPSConnection(
                    self.host,
                    self.port,
                    context=ssl._create_unverified_context(),
                    source_address=self.source_address
                )

    def _process_response(self, response, content, json_response=True):
        if self.for_app_engine:
            response.status = response.status_code

        if not json_response:
            return ApiClientResponse(response=response, content=content)
        else:
            content_json = None
            try:
                content_json = json.loads(content)
            except Exception as e:
                pass

            return ApiClientResponse(response=response, content=content_json)

    def http_get_json(self, url):
        if self.for_app_engine:
            from google.appengine.api import urlfetch
            urlfetch.set_default_fetch_deadline(URL_FETCH_DEADLINE)

            response = urlfetch.fetch(
                self.base_url + url,
                method=urlfetch.GET,
                headers=self.headers
            )
            return self._process_response(response, response.content)
        else:
            with self._get_client() as _client:
                _client.request(method="GET", url=self.base_url + url, headers=self.headers)
                _response = _client.getresponse()
                return self._process_response(_response, _response.read())

    def http_get(self, url):
        if self.for_app_engine:
            from google.appengine.api import urlfetch
            urlfetch.set_default_fetch_deadline(URL_FETCH_DEADLINE)

            response = urlfetch.fetch(
                self.base_url + url,
                method=urlfetch.GET,
                headers=self.headers
            )
            return self._process_response(response, response.content, False)
        else:
            with self._get_client() as _client:
                _client.request(method="GET", url=self.base_url + url, headers=self.headers)
                _response = _client.getresponse()
                return self._process_response(_response, _response.read(), False)

    def http_put_json(self, url, obj):
        if self.for_app_engine:
            from google.appengine.api import urlfetch
            urlfetch.set_default_fetch_deadline(URL_FETCH_DEADLINE)

            response = urlfetch.fetch(
                self.base_url + url,
                method=urlfetch.PUT,
                headers=self.headers,
                payload=json.dumps(obj)
            )
            return self._process_response(response, response.content)
        else:
            with self._get_client() as _client:
                _client.request(method="PUT", url=self.base_url + url, body=json.dumps(obj), headers=self.headers)
                _response = _client.getresponse()
                return self._process_response(_response, _response.read())

    def http_post_json(self, url, obj):
        if self.for_app_engine:
            from google.appengine.api import urlfetch
            urlfetch.set_default_fetch_deadline(URL_FETCH_DEADLINE)

            response = urlfetch.fetch(
                self.base_url + url,
                method=urlfetch.POST,
                headers=self.headers,
                payload=json.dumps(obj)
            )
            return self._process_response(response, response.content)
        else:
            with self._get_client() as _client:
                _client.request(method="POST", url=self.base_url + url, body=json.dumps(obj), headers=self.headers)
                _response = _client.getresponse()
                return self._process_response(_response, _response.read())

    def http_post(self, url, data):
        if self.for_app_engine:
            from google.appengine.api import urlfetch
            urlfetch.set_default_fetch_deadline(URL_FETCH_DEADLINE)

            response = urlfetch.fetch(
                self.base_url + url,
                method=urlfetch.POST,
                headers=self.headers,
                payload=json.dumps(data)
            )
            return self._process_response(response, response.content, json_response=False)
        else:
            with self._get_client() as _client:
                _client.request(method="POST", url=self.base_url + url, body=data, headers=self.headers)
                _response = _client.getresponse()
                return self._process_response(_response, _response.read(), json_response=False)

    def http_delete(self, url, data=None):
        if self.for_app_engine:
            from google.appengine.api import urlfetch
            urlfetch.set_default_fetch_deadline(URL_FETCH_DEADLINE)

            response = urlfetch.fetch(
                self.base_url + url,
                method=urlfetch.DELETE,
                headers=self.headers,
                payload=json.dumps(data)
            )
            return self._process_response(response, response.content)
        else:
            with self._get_client() as _client:
                _client.request(method="DELETE", url=self.base_url + url, body=data, headers=self.headers)
                _response = _client.getresponse()
                return self._process_response(_response, _response.read(), json_response=False)


class ApiClientResponse(object):
    def __init__(self, response, content):
        self.response = response
        self.content = content


class EntityClientBase(ApiClientBase):
    entity_endpoint_base_url = ''

    def __init__(self, **kwargs):
        super(EntityClientBase, self).__init__(**kwargs)
        self.scroll_id = None

    def _validate(self):
        if self.entity_endpoint_base_url == '':
            raise Exception("Must set entity_api_base_url field.")

    def get_list(self):
        self._validate()
        return self.http_get_json(self.entity_endpoint_base_url)

    def get_by_id(self, id):
        self._validate()
        return self.http_get_json(self.entity_endpoint_base_url + str(id))

    def search(self, search_info):
        self._validate()
        return self.http_post_json(self.entity_endpoint_base_url + "_search", search_info)

    def search_with_scroll(self, search_info):
        if not self.scroll_id:
            search_info.update({'use_scroll': True})
        else:
            search_info.update({'use_scroll': True, 'scroll_id': self.scroll_id})

        _result = self.search(search_info)
        _content = _result.content

        if 'extended_info' in _content and 'scroll_id' in _content['extended_info']:
            self.scroll_id = _content['extended_info']['scroll_id']
        else:
            self.scroll_id = None

        return _result

    def create(self, entity):
        self._validate()
        return self.http_post_json(self.entity_endpoint_base_url, entity)

    def bulk_create(self, entity):
        self._validate()
        return self.http_post_json(self.entity_endpoint_base_url + '_bulk-create', entity)

    def update(self, entity, id):
        self._validate()
        return self.http_put_json(self.entity_endpoint_base_url + str(id), entity)

    def delete(self, id):
        self._validate()
        return self.http_delete(self.entity_endpoint_base_url + str(id))

    def bulk_delete(self, entities_id):
        self._validate()
        return self.http_post_json(self.entity_endpoint_base_url + '_bulk-delete', entities_id)


if __name__ == '__main__':
    API_ACCESS_CONFIG = {
        'base_url': "http://localhost:8081",
        'user_name': 'webapi',
        'password': '2wsxzaq1'
    }

    API_ACCESS_CONFIG.update({'for_app_engine': False})

    client = EntityClientBase(**API_ACCESS_CONFIG)
    client.entity_endpoint_base_url = '/management/roles/'
    result = client.get_list()
    print result.response.status, result.content

    entity = result.content[0]
    result = client.update(entity, entity['name'])
    print result.response.status, result.content

