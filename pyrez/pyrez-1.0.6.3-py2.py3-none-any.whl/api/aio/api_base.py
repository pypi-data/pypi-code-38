
__all__ = (
    "APIBase",
)

#https://www.blog.pythonlibrary.org/2016/07/26/python-3-an-intro-to-asyncio/
#http://brunorocha.org/python/asyncio-o-futuro-do-python-mudou-completamente.html
#https://python-packaging.readthedocs.io/en/latest/command-line-scripts.html

class APIBase:
    def __init__(self, headers=None, cookies=None, loop=None):
        from sys import version_info
        import aiohttp
        import pyrez
        self.headers = headers or { "user-agent": "{0} [Python/{1.major}.{1.minor}.{1.micro} aiohttp/{2}]".format(pyrez.__title__, version_info, aiohttp.__version__) }
        self.cookies = cookies
        self.updateLoop(loop)
    @classmethod
    def getLoop(cls, forceFresh=False):
        """
        Parameters
        ----------
        forceFresh : |BOOL|
            Get a new loop

        Returns
        -------
        asyncio.ProactorEventLoop
            Return a loop event
        """
        import sys
        import asyncio

        # Let's not force this dependency, uvloop is much faster on cpython
        if sys.implementation.name == "cpython":
            try:
                import uvloop
            except ImportError:
                uvloop = None
            else:
                asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

        if sys.platform == 'win32' or os.name == 'nt':
            if not forceFresh and isinstance(asyncio.get_event_loop(), asyncio.ProactorEventLoop) and not asyncio.get_event_loop().is_closed():
                return asyncio.get_event_loop()
            return asyncio.ProactorEventLoop()
        if forceFresh or asyncio.get_event_loop().is_closed():
            return asyncio.new_event_loop()
        return asyncio.get_event_loop()
    def updateLoop(self, loop=None):
        import asyncio
        self.__loop = loop or self.getLoop(True)
        asyncio.set_event_loop(self.__loop)
    def closeLoop(self):
        self.__loop.close()
    async def _httpRequest(self, url, method="GET", raise_for_status=True, params=None, data=None, headers=None, cookies=None, json=None, files=None, auth=None, timeout=None, allowRedirects=False, proxies=None, hooks=None, stream=False, verify=None, cert=None):
        from json.decoder import JSONDecodeError
        import aiohttp

        async with aiohttp.ClientSession(cookies=cookies or self.cookies, headers=headers or self.headers, raise_for_status=raise_for_status) as session:
            async with session.request(method=method, url=url, params=params, data=data, json=json) as resp:
                try:
                    return await resp.json()
                except (JSONDecodeError, ValueError):
                    return await resp.text()
