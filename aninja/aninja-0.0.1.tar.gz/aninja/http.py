import asyncio
import inspect
import logging

# typing
from types import TracebackType
from typing import Any, List, Optional, Tuple, Type, Union, Mapping


from aiohttp import ClientSession
from aninja.cookies import CookiesManager
from aninja.utils import get_user_agent
from yarl import URL

_Client = 'Client'
_CSSSelector = str
_TypeIn = Tuple[_CSSSelector, str]
_URL = Union[str, URL]

logger = logging.getLogger(__name__)

DEFUALT_HEADERS = {'User-Agent': get_user_agent()}


class Request:
    """A formatted request class
    """

    def __init__(self, url, method='GET', params=None, data=None,
                 headers=None):
        self.url = url
        self.method = method
        self.params = params
        self.data = data
        self.headers = headers


class HTTPClient:
    """A client uses aiohttp to make requests.
    """

    def __init__(self,
                 cookies_manager=None,
                 **kwargs):
        self.cookies_manager: CookiesManager = cookies_manager if cookies_manager else CookiesManager()
        headers = kwargs.pop('headers', None)
        headers = headers if headers else DEFUALT_HEADERS

        self.session = ClientSession(headers=headers, **kwargs)
        self.cookies_manager.sync_to_aiohttp_session(self.session)

    async def close(self):
        await self.session.close()

    async def request(self,
                      method: str,
                      url: _URL, *,
                      params: Optional[Mapping[str, str]] = None,
                      data=None,
                      headers=None,
                      ** kwargs: Any):
        resp = await self.session.request(method, url, params=params, data=data, **kwargs)
        self.cookies_manager.update_from_aiohttp_session(self.session)
        return resp

    async def get(self, url: _URL, params=None, **kwargs: Any):
        return await self.request("GET", url, params=params, **kwargs)

    async def post(self, url: _URL, data: Any = None, params=None, **kwargs: Any):
        return await self.request("POST", url,  data=data, params=None, **kwargs)

    async def send(self, request: Request):
        resp = await self.request(method=request.method,
                                  url=request.url,
                                  params=request.params,
                                  data=request.data,
                                  headers=request.headers)
        return resp

    async def check(self, check_flag: str, url: _URL = ""):
        resp = await self.get(url)
        if check_flag in await resp.text():
            return True
        return False

    def __enter__(self) -> None:
        raise TypeError("Use async with instead")

    def __exit__(self,
                 exc_type: Optional[Type[BaseException]],
                 exc_val: Optional[BaseException],
                 exc_tb: Optional[TracebackType]) -> None:
        # __exit__ should exist in pair with __enter__ but never executed
        pass  # pragma: no cover

    async def __aenter__(self) -> 'HTTPClient':
        return self

    async def __aexit__(self,
                        exc_type: Optional[Type[BaseException]],
                        exc_val: Optional[BaseException],
                        exc_tb: Optional[TracebackType]) -> None:
        await self.close()
