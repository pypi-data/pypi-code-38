import logging
import tempfile

from contextlib import ExitStack
from pathlib import Path

import pytest

from aiohttp import ClientSession
from cryptography.hazmat.primitives import serialization

from .lib import get_proxy
from .lib.tls import make_tls_info


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture
async def client():
    async with ClientSession() as session:
        yield session
    

@pytest.fixture
def proxy(unused_tcp_port):
    with get_proxy(unused_tcp_port) as proxy_obj:
        yield proxy_obj


@pytest.fixture
def tcp_ports(unused_tcp_port_factory):
    yield unused_tcp_port_factory


@pytest.fixture
def tls_info():
    info = make_tls_info()
    with tempfile.TemporaryDirectory() as d:
        cacert_path = Path(f'{d}/cacert.pem')
        cacert_path.write_bytes(
            info.cacert.public_bytes(serialization.Encoding.PEM)
        )
        cert_path = Path(f'{d}/cert.pem')
        cert_path.write_bytes(
            info.cert.public_bytes(serialization.Encoding.PEM)
        )
        key_path = Path(f'{d}/cert.key')
        key_path.write_bytes(
            info.key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            ),
        )
        info.cacert_path = cacert_path
        info.cert_path = cert_path
        info.key_path = key_path
        yield info
