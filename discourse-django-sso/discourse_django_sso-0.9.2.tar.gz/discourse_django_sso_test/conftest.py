"""
Fixtures for all tests.
Most of the values are copied from SSO example in discourse.
"""

import pytest

from django.contrib.auth import get_user_model


# pylint: disable=missing-docstring

@pytest.fixture()
def example_user():
    return get_user_model()(
        username="foo",
        email="foo@bar.pl",
        id=1
    )


@pytest.fixture()
def example_secret():
    return b'd836444a9e4084d5b224a60c208dce14'


@pytest.fixture()
def example_sso():
    return b'bm9uY2U9Y2I2ODI1MWVlZmI1MjExZTU4YzAwZmYxMzk1ZjBjMGI=\n'


@pytest.fixture()
def example_sig():
    return b'2828aa29899722b35a2f191d34ef9b3ce695e0e6eeec47deb46d588d70c7cb56'


@pytest.fixture()
def example_producer_url():
    return 'http://example.org/sso'


@pytest.fixture()
def example_sso_url():
    return 'http://www.example.com/discourse/sso'
