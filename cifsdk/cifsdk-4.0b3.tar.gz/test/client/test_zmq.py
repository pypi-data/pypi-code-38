import py.test

from cifsdk.client.zmq import Client
from cifsdk.constants import ROUTER_ADDR


def test_zmq():
    cli = Client(ROUTER_ADDR, '12345')
    assert cli.remote == ROUTER_ADDR

    assert cli.token == '12345'
