import json
import logging
from pprint import pformat
from time import sleep

import requests
from requests import HTTPError
from six import wraps
from six.moves.urllib.parse import urljoin
from six.moves.urllib.parse import urlparse

logger = logging.getLogger(__name__)
MAX_RETRIES = 5
DEFAULT_TIMEOUT = 180


class ProviderHTTPClientException(Exception):
    def __init__(self, *args, **kwargs):
        super(ProviderHTTPClientException, self).__init__(*args)
        for key, value in kwargs:
            setattr(self, key, value)


class RetryableException(ProviderHTTPClientException):
    pass


class ProviderHTTPServiceException(ProviderHTTPClientException):
    pass


def flatten_nested_object(obj, parent_key=''):
    result = {}

    for key, value in obj.items():
        if parent_key:
            new_key = '.'.join([parent_key, key])
        else:
            new_key = key

        if isinstance(value, list):
            raise ValueError('Nesting list is not supported yet. Please change key %s' % new_key)
        if isinstance(value, dict):
            result.update(flatten_nested_object(value, new_key))
        else:
            result[new_key] = value
    return result


class ProviderRequestProxy(object):
    def __init__(self, url, headers, timeout, retries=MAX_RETRIES, host=None, retry_delay=5, **kwargs):
        self.url = url
        self.headers = headers
        self.timeout = timeout
        self.retries = retries
        self.host = host
        self.raw = kwargs.get('raw', False)
        self.is_json = kwargs.get('json', True)
        self.retry_delay = retry_delay

    def augment_request_arguments(self, **request_kwargs):
        self.headers.update(request_kwargs.get('headers', {}))
        url_override = request_kwargs.get('url', None)
        self.url = self.url.format(**request_kwargs)

        data = {
            'url': url_override if url_override else self.url,
            'headers': self.headers,
            'timeout': self.timeout,
        }
        if 'data' in request_kwargs:
            data['data'] = request_kwargs['data']
        if 'json' in request_kwargs:
            data['json'] = request_kwargs['json']
        if 'files' in request_kwargs:
            data['files'] = request_kwargs['files']
        if 'stream' in request_kwargs:
            data['stream'] = request_kwargs['stream']
        if 'params' in request_kwargs:
            data['params'] = request_kwargs['params']

        if 'json' in data and 'data' in data:
            raise ValueError('You need to use either `json` or `data` parameter, not both.')

        if ('json' in data or 'data' in data) and 'files' in data:
            # parse json or data to enable multipart
            data_payload = data.pop('json', data.pop('data', None))

            if isinstance(data_payload, str):
                data_payload = json.load(data_payload)

            if isinstance(data_payload, list):
                raise ValueError('List json is not supported with Multipart')

            data['data'] = flatten_nested_object(data_payload)

        return data

    def get(self, **request_arguments):
        return self.request_with_retry('get', **request_arguments)

    def head(self, **request_arguments):
        return self.request_with_retry('head', **request_arguments)

    def options(self, **request_arguments):
        return self.request_with_retry('options', **request_arguments)

    def post(self, **request_arguments):
        return self.request_with_retry('post', **request_arguments)

    def put(self, **request_arguments):
        return self.request_with_retry('put', **request_arguments)

    def patch(self, **request_arguments):
        return self.request_with_retry('patch', **request_arguments)

    def delete(self, **request_arguments):
        return self.request_with_retry('delete', **request_arguments)

    def format_return_data(self, response):
        if response.status_code == 204 or self.raw:
            return response
        elif self.is_json:
            try:
                return response.json()
            except ValueError as e:
                if 'JSON' not in getattr(e, 'message', ''):
                    raise
                logger.exception('Failed to decode json file with error message: %s', e)
                return {}
        else:
            return response.content()

    def request_with_retry(self, method, **request_arguments):
        request_arguments = self.augment_request_arguments(**request_arguments)
        retries = 0

        while retries < self.retries:
            try:
                response = getattr(requests, method)(**request_arguments)
                try:
                    if 400 <= response.status_code < 500:
                        http_error_msg = '%s Client Error: %s for url: %s %s' % \
                                         (response.status_code,
                                          response.reason,
                                          response.url,
                                          response.content)
                        raise ProviderHTTPClientException(http_error_msg)
                    # TODO: add more retryable exceptions code
                    elif response.status_code in [502, 503]:
                        raise RetryableException('Deployment in progress')
                    elif 500 <= response.status_code < 600:
                        response.raise_for_status()
                except HTTPError as exc:
                    logger.exception(response.content)
                    raise

            except (requests.Timeout, RetryableException):
                logger.debug('Retry request %s %s', method, request_arguments['url'])
                retries += 1
                sleep(self.retry_delay)
            except requests.ConnectionError as e:
                raise ProviderHTTPServiceException('Service is not working with error: %s' % e)
            else:
                break  # Exits while loop
        else:
            raise ProviderHTTPServiceException('Failed to do request after {} tries'.format(MAX_RETRIES))

        return self.format_return_data(response)


def remote_service(path, headers=None, timeout=None, json=True, raw=False):
    if headers is None:
        headers = {}
    assert isinstance(headers, dict), 'Headers should be a dict!'

    safe_methods = ['get', 'head', 'options']
    unsafe_methods = ['post', 'put', 'patch', 'delete']

    def wrapper(func):
        @wraps(func)
        def inner(self, *args, **kwargs):
            if not isinstance(self, ReboticsBaseProvider):
                raise TypeError('This decorator should be used only for subclasses Rebotics Base Providers')

            url = urljoin(self.host, path)
            authentication_headers = self.get_provider_headers()
            headers.update(authentication_headers)

            session = ProviderRequestProxy(url,
                                           headers,
                                           timeout=timeout or self.timeout,
                                           retries=self.retries,
                                           json=json,
                                           raw=raw,
                                           host=self.host)
            self.session = session
            return func(self, *args, **kwargs)

        return inner

    return wrapper


# noinspection PyMethodMayBeStatic
class ReboticsBaseProvider(object):
    retries = MAX_RETRIES
    timeout = DEFAULT_TIMEOUT

    def __init__(self, host, **kwargs):
        self.host = host
        self.domain = urlparse(self.host).netloc
        # TODO: add host checking

        self.headers = kwargs.get('headers', {})
        self.data = kwargs.get('data', {})
        self.session = None
        self.requests = requests

        if 'retries' in kwargs:
            self.retries = kwargs['retries']

        if 'timeout' in kwargs:
            self.timeout = kwargs['timeout']

        if 'token' in kwargs:
            self.set_token(kwargs['token'])

        self.role = kwargs.get('role', '')

    def get_provider_headers(self):
        return self.headers if self.headers else {}

    def set_header(self, key, value):
        self.headers[key] = value

    def set_token(self, token):
        self.headers['Authorization'] = 'Token %s' % token

    @remote_service('/ping/', json=False)
    def ping(self, **kwargs):
        return self.session.get()

    @remote_service('/notifications/setWebhook/')
    def set_webhook(self, url, token=None):
        """Set webhook used by rebotics_sdk.hooks and rebotics_sdk.notification apps"""
        data = {
            'url': url
        }
        if token is not None:
            data['auth_token'] = token
        return self.session.post(data=data)

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, pformat({
            'host': self.host,
            'headers': self.headers,
            'role': self.role
        }))


class PageResult(object):
    def __init__(self, json_data):
        """
        Returns paged result from rest framework
        :param dict json_data:
        """
        self.json_data = json_data

    def __len__(self):
        return self.json_data['count']

    def __iter__(self):
        for item in self.json_data['results']:
            yield item

    def __getitem__(self, item):
        return self.json_data['results'][item]

    @property
    def pdf_download_url(self):
        return self.json_data.get('pdf_url')


def required_model_params(params=None):
    if params is None:
        params = ['model_path', 'index_path', 'meta_path']

    def outer(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            model_params = {
                key: kwargs[key] for key in params
            }
            kwargs['model_params'] = {
                'model_path': model_params['model_path'],
                'model_index_path': model_params['index_path'],
                'model_meta_path': model_params['meta_path']
            }
            result = func(*args, **kwargs)
            return result

        return wrapper

    if callable(params):
        return outer(params)

    return outer
