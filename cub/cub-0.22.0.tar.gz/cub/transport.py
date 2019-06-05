from datetime import datetime
import json
import platform
import textwrap
import warnings

from .compat import string_types, binary_type
from .exceptions import *
from .timezone import utc
from .version import version


# TODO: use urlfetch for Google App Engine
try:
    import requests
    _session = requests.session()
    _lib = 'requests'
    _lib_ver = requests.__version__
except ImportError:
    warnings.warn(
        '\n\n' + textwrap.fill(
            'requests library is not available, falling to urllib2. '
            'Note that urllib2 does NOT verifies SSL certificates, so '
            'we recommend to install requests, if possible.'
        )
    )
    try:
        from urllib2 import Request, urlopen, HTTPError, URLError, \
            __version__ as urllib_ver
        _lib = 'urllib2'
        _lib_ver = urllib_ver
    except ImportError:
        from urllib.request import Request, urlopen
        from urllib.error import HTTPError, URLError
        _lib = 'urllib2'
        _lib_ver = 'internal'

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode


def urlify(params, prefix=''):
    from .models import CubObject

    def is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    result = {}
    items = params.items() if isinstance(params, dict) else enumerate(params)
    for k, v in items:
        key = '%s[%s]' % (prefix, k) if prefix else k
        if isinstance(v, (dict, list, tuple)):
            result.update(urlify(v, key))
        elif isinstance(v, bool):
            result[key] = 'true' if v else 'false'
        elif v is None:
            result[key] = 'null'
        elif isinstance(v, string_types):
            if isinstance(v, binary_type):
                # Must be utf-8, raise exception if it isn't
                v = v.decode('utf-8')
            if v in ('true', 'false', 'null') or is_number(v):
                v = '"%s"' % v
            result[key] = v
        elif isinstance(v, CubObject):
            result[key] = v.id
        else:
            result[key] = v
    return result


def json_datetime_hook(dikt):
    for k, v in dikt.items():
        if isinstance(v, string_types) and v.endswith('Z'):
            try:
                dt = datetime.strptime(v, '%Y-%m-%dT%H:%M:%SZ')
            except ValueError:
                pass
            else:
                dt = dt.replace(tzinfo=utc)
                dikt[k] = dt
    return dikt


class API(object):
    def __init__(self, key=None, base_url=None, timeout=None):
        from .config import api_key, api_url, api_timeout
        self.api_key = key or api_key
        self.base_url = base_url or api_url
        self.timeout = timeout or api_timeout

    def url(self, url):
        return '%s%s' % (self.base_url, url)

    def requests_request(self, method, url, data, headers, timeout):
        if method == 'get':
            abs_url = '%s?%s' % (url, urlencode(data))
            params = {}
        else:
            abs_url = url
            params = data
        response = _session.request(
            method,
            abs_url,
            data=params,
            headers=headers,
            timeout=timeout
        )
        http_code = response.status_code
        http_body = response.content
        return http_code, http_body

    def urllib2_request(self, method, url, data, headers, timeout):
        params = urlencode(data)
        if method == 'get':
            abs_url = '%s?%s' % (url, params)
            req = Request(abs_url, None, headers)
        elif method == 'post':
            req = Request(url, params.encode('ascii'), headers)
        elif method == 'delete':
            abs_url = '%s?%s' % (url, params)
            req = Request(abs_url, None, headers)
            req.get_method = lambda: 'DELETE'
        else:
            raise APIError('Unsupported method: %s' % method)

        try:
            response = urlopen(req, timeout=timeout)
            http_code = response.code
            http_body = response.read()
        except HTTPError as e:
            http_code = e.code
            http_body = e.read()
        return http_code, http_body

    def request(self, method, url, params=None):
        params = params or {}
        if not self.api_key:
            raise Unauthorized(
                'You did not provide an API key. There are 2 ways to do it:\n'
                '\n1) set it globally for all requests via '
                'cub.config.api_key, like this:\n'
                '\nimport cub.config\n'
                '\ncub.config.api_key = "<your-key>"\n'
                '\n'
                '\n2) pass it to methods which communicate with the API as '
                'keyword argument, like this:\n'
                '\nfrom cub import User\n'
                '\ninv = User.get(api_key="<your-key>", ...)'
            )

        abs_url = self.url(url)

        client_info = {
            'publisher': 'ivelum',
            'platform': platform.platform(),
            'language': 'Python %s' % platform.python_version(),
            'httplib': '%s v%s' % (_lib, _lib_ver)
        }

        headers = {
            'Authorization': 'Bearer %s' % self.api_key,
            'User-Agent': 'Cub Client for Python, v%s' % version,
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Cub-User-Agent-Info': json.dumps(client_info)
        }

        data = urlify(params)

        # Send request to API and handle communication errors
        if _lib == 'requests':
            try:
                http_code, http_body = self.requests_request(
                    method,
                    abs_url,
                    data=data,
                    headers=headers,
                    timeout=self.timeout
                )
            except requests.RequestException as e:
                raise ConnectionError(
                    'Cannot connect to Cub API using URL %s' % abs_url
                )
        elif _lib == 'urllib2':
            try:
                http_code, http_body = self.urllib2_request(
                    method,
                    abs_url,
                    data=data,
                    headers=headers,
                    timeout=self.timeout
                )
            except URLError as e:
                raise ConnectionError(
                    'Cannot connect to Cub API using URL %s' % abs_url
                )

        try:
            json_body = json.loads(
                http_body.decode('utf-8'),
                object_hook=json_datetime_hook,
            )
        except Exception as e:
            raise APIError(
                'Invalid response from the API: %s' % http_body,
                http_code,
                http_body
            )

        # Handle API errors
        if http_code != 200:
            try:
                error = json_body['error']
                err_desc = error['description']
                err_params = {}
                err_params.update(error.get('params', {}))
            except (KeyError, TypeError, ValueError):
                raise APIError(
                    'Invalid response from the API: %s' % json_body,
                    http_code,
                    http_body,
                    json_body
                )

            if http_code == 400:
                err_msg = err_desc
                if err_params:
                    err_msg += '\nParams:\n' + '\n'.join(
                        ['%s: %s' % (k, v) for k, v in err_params.items()]
                    )
                raise BadRequest(err_msg, http_code, http_body, json_body)
            elif http_code == 401:
                raise Unauthorized(err_desc, http_code, http_body, json_body)
            elif http_code == 403:
                raise Forbidden(err_desc, http_code, http_body, json_body)
            elif http_code == 404:
                raise NotFound(err_desc, http_code, http_body, json_body)
            elif http_code == 405:
                raise MethodNotAllowed(err_desc, http_code, http_body, json_body)
            elif http_code == 500:
                raise InternalError(err_desc, http_code, http_body, json_body)
            elif http_code == 502:
                raise BadGateway(err_desc, http_code, http_body, json_body)
            elif http_code == 503:
                raise ServiceUnavailable(
                    err_desc, http_code, http_body, json_body
                )
            else:
                raise APIError(err_desc, http_code, http_body, json_body)

        return json_body
