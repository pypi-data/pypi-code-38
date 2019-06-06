import copy
import logging
from collections import OrderedDict
from collections import namedtuple
from platform import platform, system
from sys import version_info as vi

from requests import Session
from requests.exceptions import RequestException, ConnectionError, Timeout, TooManyRedirects

from sequoia import __version__ as client_version, util
from sequoia import error, env

try:
    from distro import linux_distribution
except ImportError:
    def linux_distribution():
        return '', '', '', ''

try:
    from platform import win32_ver
except ImportError:
    def win32_ver():
        return '', '', '', ''

try:
    from platform import mac_ver
except ImportError:
    def mac_ver():
        return '', '', '', ''


class HttpExecutor:
    os_info = platform()
    os_versions = {
        'Linux': "%s (%s)" % (linux_distribution()[0], os_info),
        'Windows': "%s (%s)" % (win32_ver()[0], os_info),
        'Darwin': "%s (%s)" % (mac_ver()[0], os_info),
    }

    user_agent = 'sequoia-client-sdk-python/%s python/%s %s/%s' % (
        client_version,
        '%s.%s.%s' % (vi.major, vi.minor, vi.micro),
        system(),
        os_versions.get(system(), ''),
    )

    DEFAULT_BACKOFF_CONF = {'interval': 0, 'max_tries': 10}

    def __init__(self, auth, session=None, proxies=None, user_agent=None, get_delay=None, request_timeout=None,
                 backoff_strategy=None):
        if user_agent is not None:
            self.user_agent = user_agent + self.user_agent

        self.backoff_strategy = backoff_strategy or HttpExecutor.DEFAULT_BACKOFF_CONF

        self.get_delay = get_delay
        self.session = session or Session()
        self.session.proxies = proxies or {}
        self.session.auth = auth
        self.common_headers = {
            'User-Agent': self.user_agent,
            "Content-Type": "application/vnd.piksel+json",
            "Accept": "application/vnd.piksel+json"
        }
        self.request_timeout = request_timeout or env.DEFAULT_REQUEST_TIMEOUT_SECONDS

    @staticmethod
    def create_http_error(response):
        try:
            ret = response.json()
        except ValueError as e:
            ret = "An unexpected error occurred. HTTP Status code: %s. " % response.status_code
            ret += "Error message: %s. " % e
        return error.HttpError(ret, response.status_code)

    @staticmethod
    def return_response(response, resource_name):
        return HttpResponse(response, resource_name)

    def request(self, method, url, data=None, params=None, headers=None, retry_count=0, resource_name=None):
        import backoff

        def fatal_code(e):
            return isinstance(e, error.HttpError) and \
                   400 <= e.status_code < 500 and e.status_code != 429

        def backoff_hdlr(details):
            logging.warning('Retry `%s` for args `%s` and kwargs `%s`', details['tries'], details['args'],
                            details['kwargs'])

        decorated_request = backoff.on_exception(self.backoff_strategy.pop('wait_gen', backoff.constant),
                                                 (error.ConnectionError, error.Timeout, error.TooManyRedirects,
                                                  error.HttpError),
                                                 giveup=fatal_code,
                                                 on_backoff=backoff_hdlr,
                                                 **copy.deepcopy(self.backoff_strategy))(self._request)
        return decorated_request(method, url, data=data,
                                 params=params, headers=headers,
                                 retry_count=retry_count,
                                 resource_name=resource_name)

    def _request(self, method, url, data=None, params=None, headers=None, retry_count=0, resource_name=None):
        request_headers = util.merge_dicts(self.common_headers, headers)
        if params:
            params = OrderedDict(sorted(params.items()))

        try:
            response = self.session.request(
                method, url, data=data, params=params, headers=request_headers, allow_redirects=False,
                timeout=self.request_timeout)
        except RequestException as request_exception:
            raise self._raise_sequoia_error(request_error=request_exception)

        if response.is_redirect:
            return self.request(method, response.headers['location'], data=data, params=params, headers=request_headers,
                                retry_count=retry_count, resource_name=resource_name)

        if 400 <= response.status_code <= 600:
            self._raise_sequoia_error(response)

        return self.return_response(response, resource_name=resource_name)

    def _raise_sequoia_error(self, response=None, request_error=None):
        if isinstance(request_error, ConnectionError):
            raise error.ConnectionError(str(request_error.args[0]), cause=request_error)
        elif isinstance(request_error, Timeout):
            raise error.Timeout(str(request_error.args[0]), cause=request_error)
        elif isinstance(request_error, TooManyRedirects):
            raise error.TooManyRedirects(str(request_error.args[0]), cause=request_error)
        else:
            # error with status code
            raise self.create_http_error(response)

    def get(self, url, params=None, resource_name=None):
        return self.request('GET', url, params=params, resource_name=resource_name)

    def post(self, url, data, params=None, headers=None, resource_name=None):
        return self.request('POST', url, data=util.wrap(data, resource_name), params=params, headers=headers,
                            resource_name=resource_name)

    def put(self, url, data, params=None, headers=None, resource_name=None):
        return self.request('PUT', url, data=util.wrap(data, resource_name), params=params, headers=headers,
                            resource_name=resource_name)

    def delete(self, url, params=None, resource_name=None):
        return self.request('DELETE', url, params=params, resource_name=resource_name)


class HttpResponse(object):
    """Wraps the response object providing raw access via the
    underscore prefix, e.g. _status_code. The response data object
    is available via the _data_ property.
    """

    def __init__(self, response, resource_name=None, model_builder=None):
        self.resource_name = resource_name
        self.raw = response
        if response.text:
            self.json = response.json()
            self.full_json = self.json
            if model_builder and resource_name:
                self.model = model_builder(self.json, resource_name)
            if resource_name:
                # fixme Remove unwrapping
                self.json = util.unwrap(self.json, resource_name)
            logging.debug("Got JSON response with status code `%s`", response.status_code)

    @property
    def data(self):
        return self.full_json

    @property
    def resources(self):
        if self.resource_name:
            return self.json
        return None

    @property
    def status(self):
        return self.raw.status_code

    def to_object(self):
        json_object = self.raw.json(object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
        return getattr(json_object, self.resource_name)

    def __getattr__(self, item):
        if item.startswith("_"):
            return getattr(self.raw, item[1:])
        return self.__dict__.get(item, None)
