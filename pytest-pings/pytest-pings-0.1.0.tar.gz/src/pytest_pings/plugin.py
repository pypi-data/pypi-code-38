import typing
import pytest
from aiohttp import web


@pytest.fixture(name="pings")
def fixture_pings() -> typing.List:
    """Returns a list that telemetry_server stores Telemetry pings to."""
    return []


@pytest.fixture(name="telemetry_server")
async def fixture_telemetry_server(aiohttp_server, pings: typing.List):
    """Return a TestServer that stores Telemetry pings to the pings fixture.

    Submit pings via POST /submit/telemetry/{id}/{type}/
    """

    async def submit(request):
        """Handler that stores Telemetry pings."""
        pings.append(await request.json())
        return web.Response(status=200)

    app = web.Application()
    app.add_routes([web.post("/submit/telemetry/{id}/{type}/{info:.*}", submit)])
    return await aiohttp_server(app)
