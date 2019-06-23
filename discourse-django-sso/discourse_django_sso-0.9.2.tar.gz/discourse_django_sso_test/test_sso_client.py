"""Test SSOClientUtils."""

import pytest
from discourse_django_sso.views import InMemoryNonceService, NonceService
from discourse_django_sso.utils import SSOClientUtils


# pylint: disable=missing-docstring,redefined-outer-name,invalid-name


@pytest.fixture()
def sso_client(
        example_secret,
        example_sso_url,
):
    return SSOClientUtils(
        sso_key=example_secret,
        base_sso_url=example_sso_url,
    )


def test_get_sso_redirect(sso_client: SSOClientUtils):
    # expected = 'http://www.example.com/discourse/sso?' \
    #            'sso=bm9uY2U9Y2I2ODI1MWVlZmI1MjExZTU4YzAwZmYxMzk1ZjBjMGI%3D%0A&' \
    #            'sig=2828aa29899722b35a2f191d34ef9b3ce695e0e6eeec47deb46d588d70c7cb56'
    expected = 'http://www.example.com/discourse/sso?' \
               'sso=bm9uY2U9Y2I2ODI1MWVlZmI1MjExZTU4YzAwZmYxMzk1ZjBjMGI%3D&' \
               'sig=1ce1494f94484b6f6a092be9b15ccc1cdafb1f8460a3838fbb0e0883c4390471'
    actual = sso_client.generate_sso_url(b'cb68251eefb5211e58c00ff1395f0c0b', False)
    assert expected == actual


def test_sso_redirect_activation_req(sso_client: SSOClientUtils):
    """
    Should generate redirect url for sso when require_activation is true
    :param sso_client:
    :return:
    """
    expected = 'http://www.example.com/discourse/sso?' \
               'sso=bm9uY2U9Y2I2ODI1MWVlZmI1MjExZTU4YzAwZmYxMzk1ZjBjMGImcmVxdWlyZV9hY3RpdmF0aW' \
               '9uPXRydWU%3D&' \
               'sig=d6fe1e49e146c1487d06fb8acfb6ed77a31575e715d18daaa19ff8f2f43576d8'
    actual = sso_client.generate_sso_url(b'cb68251eefb5211e58c00ff1395f0c0b', True)
    assert expected == actual


def test_decode_sso_data(sso_client: SSOClientUtils):
    user_data = sso_client.decode_client_data(
        b'bm9uY2U9Y2I2ODI1MWVlZmI1MjExZTU4YzAwZmYxMzk1ZjBjMGImbmFtZT1zYW0mdXNlcm5hbWU9\nc2Ftc2FtJm'
        b'VtYWlsPXRlc3QlNDB0ZXN0LmNvbSZleHRlcm5hbF9pZD1oZWxsbzEyMyZyZXF1aXJl\n'
        b'X2FjdGl2YXRpb249dHJ1ZQ==\n')
    print('MIK' + sso_client.get_param(user_data, 'nonce'))
    assert sso_client.get_param(user_data, b'nonce') == 'cb68251eefb5211e58c00ff1395f0c0b'


def test_sid_sso_validation(sso_client: SSOClientUtils):
    assert sso_client.validate_sso_against_sid(
        b'bm9uY2U9Y2I2ODI1MWVlZmI1MjExZTU4YzAwZmYxMzk1ZjBjMGImbmFtZT1zYW0mdXNlcm5hbWU9\nc2Ftc2FtJm'
        b'VtYWlsPXRlc3QlNDB0ZXN0LmNvbSZleHRlcm5hbF9pZD1oZWxsbzEyMyZyZXF1aXJl\nX2FjdGl2YXRpb249dHJ1'
        b'ZQ==\n', b'3a8dd1a73254003d616d610f66049cf741dfcb924c76b9e75efa01b2507ad0d0') is True


@pytest.fixture()
def nonce_service():
    return InMemoryNonceService()


def test_generate_nonce(nonce_service: NonceService):
    nonce = nonce_service.generate_nonce()
    assert nonce is not None


def test_invalidate_nonce(nonce_service: NonceService):
    nonce = nonce_service.generate_nonce()
    assert nonce_service.is_nonce_valid(nonce) is True
    nonce_service.invalidate_nonce(nonce)
    assert nonce_service.is_nonce_valid(nonce) is False


def test_nonce_valid_for_not_existing_nonce(nonce_service: NonceService):
    assert nonce_service.is_nonce_valid('NOT_GENERATED_VALUE') is False
