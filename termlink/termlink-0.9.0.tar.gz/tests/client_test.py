"""Validates the 'client.py" module"""

from nose.tools import ok_, eq_, raises

from requests_mock import Adapter

from termlink.client import Client


def test_client_construction():
    """Checks that the client can be instantiated"""
    url = 'url'
    client = Client(url)
    ok_(client)

@raises(TypeError)
def test_url_is_required():
    """Checks that the url parameter is required"""
    client = Client(url=None)

def test_mocking_client_adapter():
    """Checks that mocking the client adapter is possible"""

    url = 'http://mock.com'

    adapter = Adapter()
    client = Client(url=url, adapter=adapter)

    exp = 'success'
    adapter.register_uri('GET', url, text=exp)
    res = client.request('get')

    eq_(200, res.status_code)
    eq_(exp, res.text)


def test_rate_limit():
    """Checks that the rate limit is working"""

    url = 'http://mock.com'

    adapter = Adapter()
    client = Client(url=url, adapter=adapter)

    exp = 'success'
    adapter.register_uri('GET', url, text=exp)
    res = client.request('get')

    eq_(200, res.status_code)
    eq_(exp, res.text)
