"""Provides client libraries for communicating with the LifeOmic API"""

from urllib.parse import urljoin, urlparse

from ratelimit import limits, RateLimitException
from backoff import on_exception, expo

from requests import Session

from termlink.adapter import DEFAULT as DEFAULT_ADAPTER
from termlink.configuration import Config


_DEFAULT_RATE_LIMIT = 10
_DEFAULT_RATE_LIMIT_PERIOD = 1
_DEFAULT_RATE_LIMIT_MAX_RETRIES = 3

_configuration = Config()

_rate_limit = int(_configuration.get_property('API_RATE_LIMIT', _DEFAULT_RATE_LIMIT))
_rate_limit_period = int(_configuration.get_property('API_RATE_LIMIT_PERIOD', _DEFAULT_RATE_LIMIT_PERIOD))
_rate_limit_max_retries = int(_configuration.get_property('API_RATE_LIMIT_MAX_RETIRES', _DEFAULT_RATE_LIMIT_MAX_RETRIES))


class Client:
    """An HTTP client"""

    def __init__(
            self,
            url,
            adapter=DEFAULT_ADAPTER):
        """
        Creates a new API client.

        Args:
            adapter (HTTPAdapter):  an HTTPAdapter
        """

        if url is None:
            raise TypeError("'url' is required")

        session = Session()

        parsed = urlparse(url)
        prefix = parsed[0] + "://"
        session.mount(prefix, adapter)

        self.session = session
        self.url = url

    @on_exception(expo, RateLimitException, max_tries=_rate_limit_max_retries)
    @limits(calls=_rate_limit, period=_rate_limit_period)
    def request(self, method, path=None, data=None):
        """
        A facade around :func:`requests.request` that provides rate limiting.

        Args:
            method: request method
            path:   URL path
            data:   JSON  data

        Returns:
            A :class:`Response <Response>` object
        """
        url = urljoin(self.url, path) if path else self.url
        return self.session.request(method, url, json=data)
