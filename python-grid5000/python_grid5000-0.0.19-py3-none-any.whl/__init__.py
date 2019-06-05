import copy

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

import yaml

from .exceptions import * # noqa
from .objects import * # noqa


DEFAULT_BASE_URL = 'https://api.grid5000.fr/stable'
USER_AGENT = 'python-grid5000'


def _create_session(retries=5,
                    backoff_factor=0.3,
                    status_forcelist=(500, 502, 504),
                    session=None):
    session = session or requests.Session()

    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )

    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    return session


class Grid5000(object):
    """Represents a Grid5000 API connection.

    Args:
        uri (str): The URL of the Grid5000 api.
        username (str): The user login.
        password (str): The user password.
        verify_ssl (bool); Whether SSL certificates should be validated.
        timeout (float): Timeout to use for requests to the Grid5000 API.
        session (requests.Session): session to use
    """

    def __init__(self, *,
               uri=DEFAULT_BASE_URL,
               username=None,
               password=None,
               verify_ssl=True,
               timeout=None,
               session=None,
               **kwargs):
        self._uri = uri
        self.timeout = timeout
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl

        self.headers = {'user-agent': USER_AGENT}
        self.session = _create_session()

        # manage auth
        self._http_auth = None
        if self.username:
            self._http_auth = requests.auth.HTTPBasicAuth(self.username,
                                                          self.password)

        self.root = RootManager(self)
        self.sites = SiteManager(self)

    @classmethod
    def from_yaml(cls, yaml_file):
        with open(yaml_file, "r") as f:
            conf = yaml.load(f)
        return cls(**conf)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return self.session.cloase()

    def _build_url(self, path):
        """Returns the full url from path.

        If path is already a url, return it unchanged. If it's a path, append
        it to the stored url.

        Returns:
            str: The full URL
        """
        if path.startswith('http://') or path.startswith('https://'):
            return path
        else:
            return '%s%s' % (self._uri, path)

    def _get_session_opts(self, content_type=None, accept=None):
        request_headers = self.headers.copy()
        if content_type is not None:
            request_headers['Content-type'] = content_type
        if accept is not None:
            request_headers['Accept'] = accept

        return {
            'headers': request_headers,
            'auth': self._http_auth,
            'timeout': self.timeout,
            'verify': self.verify_ssl
        }

    def http_request(self, verb, path, query_data=None, post_data=None,
                     streamed=False,
                     content_type="application/json",
                     accept="application/json",
                     **kwargs):
        """Make an HTTP request to the Grid5000 API.

        Args:
            verb (str): The HTTP method to call ('get', 'post', 'put',
                        'delete')
            path (str): Path or full URL to query ('/sites' or
                        'http://api.grid5000.fr/stable/sites')
            query_data (dict): Data to send as query parameters
            post_data (dict): Data to send in the body (will be converted to
                              json)
            streamed (bool): Whether the data should be streamed
            **kwargs: Extra options to send to the server (e.g. sudo)

        Returns:
            A requests result object.

        Raises:
            Grid5000HttpError: When the return code is not 2xx
        """
        query_data = {} if query_data is None else query_data
        url = self._build_url(path)

        opts = self._get_session_opts(content_type=content_type,
                                      accept=accept)

        verify = opts.pop('verify')
        timeout = opts.pop('timeout')

        json = post_data
        data = None

        # building params from query params and kwargs
        params = {}
        params = copy.deepcopy(query_data)
        params.update(kwargs)

        req = requests.Request(verb, url,
                               json=json,
                               data=data,
                               params=params,
                               **opts)
        prepped = req.prepare()

        settings = self.session.merge_environment_settings(
            prepped.url, {}, streamed, verify, None)

        while True:
            result = self.session.send(prepped, timeout=timeout, **settings)

            # TODO:
            # https://www.grid5000.fr/mediawiki/index.php/API#Status_Codes
            if 200 <= result.status_code < 300:
                return result

            error_message = result.content
            try:
                error_json = result.json()
                for k in ('message', 'error'):
                    if k in error_json:
                        error_message = error_json[k]
            except (KeyError, ValueError, TypeError):
                pass

            if result.status_code == 401:
                raise Grid5000AuthenticationError(
                    response_code=result.status_code,
                    error_message=error_message,
                    response_body=result.content)

            raise Grid5000HttpError(response_code=result.status_code,
                                  error_message=error_message,
                                  response_body=result.content)

    def http_get(self, path, query_data={}, streamed=False, raw=False,
                 **kwargs):
        """Make a GET request to the Grid5000 server.

        Args:
            path (str): Path or full URL to query ('/projects' or
                        'http://whatever/v4/api/projecs')
            query_data (dict): Data to send as query parameters
            streamed (bool): Whether the data should be streamed
            raw (bool): If True do not try to parse the output as json
            **kwargs: Extra options to send to the server (e.g. sudo)

        Returns:
            A requests result object is streamed is True or the content type is
            not json.
            The parsed json data otherwise.

        Raises:
            Grid5000HttpError: When the return code is not 2xx
            Grid5000ParsingError: If the json data could not be parsed
        """
        result = self.http_request('get', path, query_data=query_data,
                                   streamed=streamed, **kwargs)

        # NOTE(msimonin): Grid5000 API is returning
        # 'application/json; charset=utf-8'
        if ('application/json' in result.headers['Content-Type']
           and not streamed
           and not raw):
            try:
                return result.json()
            except Exception:
                raise Grid5000ParsingError(
                    error_message="Failed to parse the server message")
        else:
            return result

    def http_list(self, path, query_data={}, **kwargs):
        """Make a GET request to the Grid5000 API for list-oriented queries.

        Args:
            path (str): Path or full URL to query ('/sites' or
                        'https://base_url/sites')
            query_data (dict): Data to send as query parameters
            **kwargs: Extra options to send to the server (e.g. sudo, page,
                      per_page)

        Returns:
            list: A list of the objects returned by the server.

        Raises:
            Grid5000HttpError: When the return code is not 2xx
            Grid5000ParsingError: If the json data could not be parsed
        """
        url = self._build_url(path)

        result = self.http_request("get", url,
                                   query_data=query_data,
                                   **kwargs)

        # NOTE(msimonin): in the future we may want to support automatic
        # pagination Thus we'll need to return an iterator here (in a generic
        # way ...)

        # NOTE(msimonin): here we hit the HATEOAS vs non HATEOAS hell
        result = result.json()
        if "items" in result:
            return result["items"]
        else:
            return result

    def http_post(self, path,
                  query_data={},
                  post_data={},
                  **kwargs):
        """Make a POST request to the Grid5000 server.

        Args:
            path (str): Path or full URL to query ('/sites' or
                        'https://api.grid5000.fr/stable/sites')
            query_data (dict): Data to send as query parameters
            post_data (dict): Data to send in the body (will be converted to
                              json)
            **kwargs: Extra options to send to the server (e.g. sudo)

        Returns:
            The parsed json returned by the server if json is return, else the
            raw content

        Raises:
            Grid5000HttpError: When the return code is not 2xx
            Grid5000ParsingError: If the json data could not be parsed
        """
        result = self.http_request('post', path, query_data=query_data,
                                   post_data=post_data, **kwargs)
        try:
            # NOTE(msimonin): Grid5000 API is returning
            # 'application/json; charset=utf-8'
            if 'application/json' in result.headers['Content-Type']:
                return result.json()
        except Exception:
            raise Grid5000ParsingError(
                error_message="Failed to parse the server message")
        return result

    def http_delete(self, path, **kwargs):
        """Make a DELETE request to the Grid5000 server.

        Args:
            path (str): Path or full URL to query ('/projects' or
                        'http://whatever/v4/api/projecs')
            **kwargs: Extra options to send to the server (e.g. sudo)

        Returns:
            The requests object.

        Raises:
            Grid5000HttpError: When the return code is not 2xx
        """
        return self.http_request('delete', path, content_type=None, **kwargs)
