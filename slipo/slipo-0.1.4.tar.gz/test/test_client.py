"""
Test for :py:mod:`slipo.client` module
"""
import unittest

from context import Client, SlipoException  # pylint: disable=import-error

from secret import BASE_URL, API_KEY


class TestClient(unittest.TestCase):

    def test_client_requires_ssl_true(self):
        def create(): return Client(
            api_key=API_KEY,
            base_url='http://127.0.0.1',
        )

        self.assertRaises(SlipoException, create)

    def test_client_requires_ssl_false(self):
        def create(): return Client(
            api_key=API_KEY,
            base_url='http://127.0.0.1',
            requires_ssl=False,
        )

        self.assertWarns(UserWarning, create)


if __name__ == '__main__':
    unittest.main()
