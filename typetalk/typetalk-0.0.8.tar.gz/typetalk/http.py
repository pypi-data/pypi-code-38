# Standard Imports
import json

# ThirdParty Imports
import aiohttp

async def json_or_text(response):
    text = await response.text(encoding='utf-8')
    if response.headers['content-type'] == 'application/json':
        return json.loads(text)
    return text


class Route:
    BASE = 'https://typetalk.com'

    def __init__(self, method, path, **parameters):
        self.method = method
        self.path = path
        url = '{}{}'.format(self.BASE, self.path)


class HTTPClient:
    """Represents an HTTP client sending HTTP requests to the Typetalk API."""

    def init(self):
        self.__session = None  # filled in static_login
        self.token = None
        self.is_bot = False

    async def request(self, route, **kwargs):
        method = route.method
        url = route.url

        headers = {}

        if self.is_bot:
            headers['X-Typetalk-Token'] = self.token
        else:
            headers['Authorization'] = "Bearer {}".format(self.token)

        kwargs['headers'] = headers

        async with self.__session.request(method, url, **kwargs) as r:
            data = await json_or_text(r)
            return data
