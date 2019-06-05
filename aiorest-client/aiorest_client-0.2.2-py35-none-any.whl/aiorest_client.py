"""Make REST calls simplier."""

import copy
import inspect
import posixpath
import asyncio
import logging
import aiohttp
from aiohttp.web import HTTPError


__author__ = "Kirill Klenov"
__author_email__ = "horneds@gmail.com"
__version__ = "0.2.2"
__license__ = "MIT license"


AIOHTTP_OPTIONS = set(inspect.signature(aiohttp.client.ClientSession._request).parameters)


def acoro(value):
    async def coro():
        return value


class APIError(HTTPError):
    """An API exception."""

    def __init__(self, reason=None, status_code=500, **kwargs):
        """Dynamically set status code."""
        self.status_code = status_code
        super(APIError, self).__init__(reason=reason,  **kwargs)


class APIDescriptor(object):
    """Keep a request's information."""

    __methods = 'GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD'

    def __init__(self, request, method='GET', path=None, root=None):
        """Initialize the descriptor."""
        self.__request = request
        self.__path = [] if path is None else path
        self.__root = root or ''

        method = method.upper()
        self.__method = method if method in self.__methods else 'GET'

    def __getitem__(self, piece):
        """Prepare a request."""
        return APIDescriptor(
            self.__request, self.__method, self.__path + [str(piece).strip('/')], self.__root)

    def __getattr__(self, name):
        """Prepare a request."""
        method = str(name).upper()
        if method in self.__methods:
            self.__method = method
            return self
        return self[name]

    @property
    def url(self):
        """Return self url."""
        return "%s%s" % (self.__root, "/" + "/".join(self.__path))

    def __str__(self):
        """String representation."""
        return "%s %s" % (self.__method, self.url)

    def __repr__(self):
        """Internal representation."""
        return 'URL: %s' % self

    def __call__(self, *body, **opts):
        """Prepare a request."""
        if body:
            opts['params' if self.__method == 'GET' else 'data'] = body[0]

        return self.__request(self.__method, self.url, **opts)


class APIClient:
    """Working with an API."""

    Error = APIError

    def __init__(self, root_url, parse=True, timeout=10, logger=None,
                 session=None, json=True, **defaults):
        """Initialize the client."""
        self.root_url = root_url
        self.middlewares = []
        self.session = session
        self.defaults = defaults
        self.parse = parse
        self.timeout = timeout
        self.json = json

        self.logger = logger or logging.getLogger(__name__)

    def __str__(self):
        return self.root_url

    def __repr__(self):
        return "<APIClient %s>" % self

    async def startup(self, app=None):
        """Initialize the client."""
        self.session = self.session or aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout))

    async def cleanup(self, app=None):
        """Cleanup the client."""
        if self.session:
            await self.session.close()

    @property
    def api(self):
        """Return API descriptor."""
        return APIDescriptor(self.request, root=self.root_url)

    def middleware(self, corofunc):
        """Register a given middleware."""
        if not asyncio.iscoroutinefunction(corofunc):
            raise ValueError('Middleware "%s" must be a coroutine function.' % corofunc.__name__)

        self.middlewares.insert(0, corofunc)
        return corofunc

    async def request(self, method, url, session=None, **options):
        """Do a request."""

        session = session or self.session
        if not session:
            raise APIError('The client is not initialized.')

        if not isinstance(session, aiohttp.ClientSession):
            session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout))

        # Process defaults
        for opt, val in self.defaults.items():
            if opt not in options:
                options[opt] = copy.copy(val)
            elif isinstance(val, dict):
                options[opt] = dict(self.defaults[opt], **options[opt])

        data, json = options.get('data'), options.get('json')
        if self.json and json is None and data is not None:
            options['json'], options['data'] = data, None

        # Process middlewares
        for middleware in self.middlewares:
            method, url, options = await middleware(method, url, options)

        if not url.startswith('http'):
            url = posixpath.join(self.root_url, url.lstrip('/'))

        req_opts = {k: v for k, v in options.items() if k in AIOHTTP_OPTIONS}
        self.logger.info("%s: %s %r" % (method.upper(), url, req_opts))

        response = None
        try:
            silent = options.get('silent')
            response = await session.request(method, url, **req_opts)
            if not silent and (response.status / 200 > 2):
                reason = await response.text()
                self.logger.error(reason)
                raise APIError(reason, response.status)

        except asyncio.TimeoutError:
            response = 524
            if not silent:
                raise APIError('Timeout Error', response)

            return None

        finally:
            callback = options.get('callback')
            if callback:
                await callback(method, url, options, response=response)

        self.logger.info('Response %s: %r' % (response.status, response.headers))
        if options.get('close'):
            response.close()
            return response

        if options.get('parse', self.parse):
            return await self.parse_response(response)

        return response

    def parse_response(cls, response):
        """Parse body for given response by content-type.

        :returns: a parser's coroutine
        """
        ct = response.headers.get('content-type', '')
        if ct.startswith('application/json'):
            try:
                return response.json()
            except ValueError:
                return response.text()

        if ct.startswith('multipart'):
            return response.post()

        return response.text()
