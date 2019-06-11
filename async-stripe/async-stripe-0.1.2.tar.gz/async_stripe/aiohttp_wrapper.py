from contextlib import asynccontextmanager
from aiohttp_params import session_complex_params
import asynctools

# TODO: make a package out of this or just add it to async-tools, also rename the repo to aiohttp-api-wrapper
class APIWrapper(asynctools.AbstractSessionContainer):
    def __init__(self, handle_complex_params=True, **kwargs):
        super().__init__(**kwargs)
        self._handle_complex_params = handle_complex_params

    async def session_hook(self, session):
        if self._handle_complex_params:
            return session_complex_params(session)
        else:
            return session

    @asynccontextmanager
    @asynctools.attach_session
    async def post(self, url, session=None, params=None, **kwargs):
        params = _remove_nones(params)
        async with session.post(url, params=params, **kwargs) as response:
            yield response

    @asynccontextmanager
    @asynctools.attach_session
    async def get(self, url, session=None, params=None, **kwargs):
        params = _remove_nones(params)
        async with session.get(url, params=params, **kwargs) as response:
            yield response


def _remove_nones(dictionary):
    try:
        return {k: v for k, v in dictionary.items() if v is not None}
    except AttributeError:
        return dictionary