import logging
import os
import ssl
import threading
import uuid

from contextlib import asynccontextmanager, AsyncExitStack, contextmanager, ExitStack

import asyncio
import pytest
import requests_async as requests

from aiohttp import ClientRequest, ClientSession, hdrs, web

from reverse_forward_proxy import DEFAULT_TARGET_HEADER, ENV_SSL_CERT_FILE
from reverse_forward_proxy.server import make_server as _make_server

from .lib import poll


pytestmark = pytest.mark.asyncio


os.environ['PYTHONASYNCIODEBUG'] = '1'


logger = logging.getLogger(__name__)


@pytest.fixture
async def backend_server(make_aiohttp_server):
    app = web.Application()

    async def root(request):
        return web.Response(text='example')

    app.router.add_get('/', root)

    yield await make_aiohttp_server(app)


@pytest.fixture
async def make_aiohttp_server(aiohttp_server):
    @asynccontextmanager
    async def _make_server(app: web.Application, **kwargs):
        server = await aiohttp_server(app, **kwargs)

        try:
            yield server
        finally:
            # Required otherwise it complains about unwaited task.
            await server.close()

    async def inner(app: web.Application, **kwargs):
        return await stack.enter_async_context(_make_server(app, **kwargs))

    stack = AsyncExitStack()

    async with stack:
        yield inner


async def test_test_proxy(client, proxy, backend_server):
    # Ensure test proxy server works as expected.
    async with client.get(backend_server.make_url('/'), proxy=proxy.address) as resp:
        assert await resp.text() == 'example'

    assert len(proxy.events)


@contextmanager
def make_test_server(address, *args, **kwargs):
    server = _make_server(address, *args, **kwargs)
    t = threading.Thread(target=server.serve_forever)
    t.daemon = True
    t.start()

    assert poll(address), "Server did not come up"

    try:
        yield server
    finally:
        server.shutdown()
        t.join()


@pytest.fixture
def test_server(proxy, tcp_ports):
    test_server_port = tcp_ports()

    with make_test_server(
        ('localhost', test_server_port), proxy.address
    ) as server:
        server.address = f'http://localhost:{test_server_port}'
        yield server


async def test_proxy(client, test_server, proxy, backend_server):
    # Given an http proxy
    # And a server behind it
    # And the proxy is brought up
    # When a request comes in with the expected header
    # Then it will be routed to the specified server
    # And a response will be returned to the client
    headers = {
        DEFAULT_TARGET_HEADER: str(backend_server.make_url('/')),
    }

    url1 = f'{test_server.address}/'
    async with client.get(url1, headers=headers) as resp:
        assert await resp.text() == 'example', f"Expected example response: {resp}"

    assert len(proxy.events) == 2

    # TODO: Assert that headers are as-expected (should be saved by server).


async def test_when_forward_proxy_not_up(client, backend_server, tcp_ports):
    # Given the proxy is up
    # And the http proxy is not up
    # When a request comes in
    # Then it should be given a 502 response
    headers = {
        DEFAULT_TARGET_HEADER: str(backend_server.make_url('/')),
    }

    fake_proxy_port = tcp_ports()
    proxy_address = f'http://127.0.0.1:{fake_proxy_port}'
    reverse_proxy_port = tcp_ports()

    with make_test_server(
        ('localhost', reverse_proxy_port), proxy_address
    ) as test_server:
        address = f'http://localhost:{reverse_proxy_port}'
        url1 = f'{address}/'
        async with client.get(url1, headers=headers) as resp:
            assert resp.status == 502


async def test_when_backend_not_up(client, test_server, tcp_ports):
    # Given the proxy is up
    # And the http proxy is up
    # And the backend server is down
    # When a request comes in
    # Then it should be given a 502 response
    fake_backend_port = tcp_ports()

    headers = {
        DEFAULT_TARGET_HEADER: f'http://localhost:{fake_backend_port}/',
    }

    url = f'{test_server.address}/'
    async with client.get(url, headers=headers) as resp:
        assert resp.status == 502


@pytest.mark.skip(reason='not implemented')
async def test_when_backend_slow(client, make_aiohttp_server, tcp_ports):
    # Given the proxy is up
    # And the http proxy is up
    # When a request comes in
    # And the backend server takes longer than the test server timeout
    # Then a 504 response should be returned
    ...


async def test_proxy_with_chunked_response(client, test_server, make_aiohttp_server):
    # Given the proxy is up
    # And the http proxy is up
    # When a request comes in
    # And the response is chunked
    # Then the expected response will be returned
    app = web.Application()

    async def root(request):
        resp = web.StreamResponse()
        resp.enable_chunked_encoding()
        await resp.prepare(request)
        await resp.write(b'example')
        await resp.write_eof()
        return resp

    app.router.add_get('/', root)

    server = await make_aiohttp_server(app)

    headers = {
        DEFAULT_TARGET_HEADER: str(server.make_url('/')),
    }

    url1 = f'{test_server.address}/'
    async with client.get(url1, headers=headers) as resp:
        assert await resp.text() == 'example', f"Expected example response: {resp}"
        assert 'chunked' in resp.headers['transfer-encoding']
        assert 'content-encoding' not in resp.headers


async def test_proxy_with_chunked_gzip_response(
    client, test_server, proxy, make_aiohttp_server
):
    # Given the proxy is up
    # And the http proxy is up
    # When a request comes in
    # And the response is chunked
    # And the response is gzip compressed
    # Then the expected response will be returned
    app = web.Application()

    async def root(request):
        logger.debug('Got request')
        assert 'gzip' in request.headers['accept-encoding']
        resp = web.StreamResponse()
        resp.enable_compression(force=web.ContentCoding.gzip)
        resp.enable_chunked_encoding()
        await resp.prepare(request)
        await resp.write(b'example')
        await resp.write_eof()
        return resp

    app.router.add_get('/', root)

    backend_server = await make_aiohttp_server(app)

    headers = {
        DEFAULT_TARGET_HEADER: str(backend_server.make_url('/')),
    }

    url1 = f'{test_server.address}/'
    async with client.get(url1, headers=headers) as resp:
        assert await resp.text() == 'example', f"Expected example response: {resp}"
        assert 'chunked' in resp.headers['transfer-encoding']
        assert 'gzip' in resp.headers['content-encoding']

    assert len(proxy.events) == 2


async def test_proxy_forwards_path(client, test_server, make_aiohttp_server):
    app = web.Application()

    param = str(uuid.uuid4())

    async def root(request):
        return web.Response(text=str(request.path))

    app.router.add_get('/{param}', root)

    backend_server = await make_aiohttp_server(app)

    headers = {
        DEFAULT_TARGET_HEADER: str(backend_server.make_url('/')),
    }

    url1 = f'{test_server.address}/{param}'
    async with client.get(url1, headers=headers) as resp:
        assert resp.status == 200
        assert await resp.text() == f'/{param}', f"Expected example response: {resp}"


async def test_proxy_forwards_params(client, test_server, make_aiohttp_server):
    app = web.Application()

    param = str(uuid.uuid4())

    async def root(request):
        return web.Response(text=request.query['id'])

    app.router.add_get('/', root)

    backend_server = await make_aiohttp_server(app)

    headers = {
        DEFAULT_TARGET_HEADER: str(backend_server.make_url('/')),
    }

    url1 = f'{test_server.address}/?id={param}'
    async with client.get(url1, headers=headers) as resp:
        assert resp.status == 200
        assert await resp.text() == param, f"Expected example response: {resp}"

    # TODO: params requiring encoding.


async def test_proxy_forwards_headers(client, test_server, make_aiohttp_server):
    app = web.Application()

    param = str(uuid.uuid4())

    async def root(request):
        return web.Response(text=request.headers['example'])

    app.router.add_get('/', root)

    backend_server = await make_aiohttp_server(app)

    headers = {
        DEFAULT_TARGET_HEADER: str(backend_server.make_url('/')),
        'example': param,
    }

    url = f'{test_server.address}/'
    async with client.get(url, headers=headers) as resp:
        assert resp.status == 200
        assert await resp.text() == param, f"Expected example response: {resp}"


async def test_proxy_returns_headers(client, test_server, make_aiohttp_server):
    app = web.Application()

    param = str(uuid.uuid4())

    async def root(request):
        return web.Response(text='hello', headers={'header': param})

    app.router.add_get('/', root)

    backend_server = await make_aiohttp_server(app)

    headers = {
        DEFAULT_TARGET_HEADER: str(backend_server.make_url('/')),
    }

    url = f'{test_server.address}/'
    async with client.get(url, headers=headers) as resp:
        assert resp.status == 200
        assert resp.headers['header'] == param, f"Expected example response: {resp}"


async def test_proxy_respects_target_header(
    client, proxy, make_aiohttp_server, tcp_ports
):
    app = web.Application()

    async def root(request):
        return web.Response(text='hello')

    app.router.add_get('/', root)

    backend_server = await make_aiohttp_server(app)

    test_server_port = tcp_ports()

    test_target_header = 'X-Test-Target-Header'

    headers = {
        test_target_header: str(backend_server.make_url('/')),
    }

    with make_test_server(
        ('localhost', test_server_port), proxy.address, target_header=test_target_header
    ) as test_server:
        test_server.address = f'http://localhost:{test_server_port}'
        url = f'{test_server.address}/'
        async with client.get(url, headers=headers) as resp:
            assert resp.status == 200


async def test_proxy_respects_ca_file(
    client, tls_info, proxy, make_aiohttp_server, tcp_ports, monkeypatch
):
    app = web.Application()

    async def root(request):
        return web.Response(text='hello')

    app.router.add_get('/', root)

    ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ctx.load_cert_chain(tls_info.cert_path, tls_info.key_path)
    backend_server = await make_aiohttp_server(app, ssl=ctx)

    headers = {
        DEFAULT_TARGET_HEADER: str(backend_server.make_url('/')),
    }

    monkeypatch.setenv(ENV_SSL_CERT_FILE, str(tls_info.cacert_path))

    test_server_port = tcp_ports()

    with make_test_server(
        ('localhost', test_server_port), proxy.address
    ) as test_server:
        test_server.address = f'http://localhost:{test_server_port}'
        url = f'{test_server.address}/'
        async with client.get(url, headers=headers) as resp:
            assert resp.status == 200


async def test_proxy_rejects_unknown_ca_cert(
    client, tls_info, test_server, make_aiohttp_server
):
    app = web.Application()

    async def root(request):
        return web.Response(text='hello')

    app.router.add_get('/', root)

    ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ctx.load_cert_chain(tls_info.cert_path, tls_info.key_path)
    backend_server = await make_aiohttp_server(app, ssl=ctx)

    headers = {
        DEFAULT_TARGET_HEADER: str(backend_server.make_url('/')),
    }

    url = f'{test_server.address}/'
    async with client.get(url, headers=headers) as resp:
        assert resp.status == 503
