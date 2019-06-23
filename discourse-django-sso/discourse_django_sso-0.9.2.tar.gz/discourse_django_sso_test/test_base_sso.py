# coding=utf-8

"""Tests for base SSO generator."""

import base64
from urllib.parse import parse_qs, unquote

import pytest

from discourse_django_sso import utils

# pylint: disable=missing-docstring
# pylint: disable=protected-access,redefined-outer-name


@pytest.fixture()
def base_generator(example_secret):
    return utils.BaseSSOGenerator(example_secret)


def test_signature(base_generator, example_sso, example_sig):
    assert base_generator._get_payload_singature(example_sso) == example_sig


def test_verify_payload(base_generator, example_sso, example_sig):
    assert base_generator._verify_payload(example_sso, example_sig)
    assert base_generator._verify_payload(example_sso.decode('ascii'), example_sig)
    assert base_generator._verify_payload(example_sso, example_sig.decode('ascii'))
    assert base_generator._verify_payload(example_sso.decode('ascii'), example_sig.decode('ascii'))


def test_verify_payload_negative(base_generator, example_sso, example_sig):
    assert not base_generator._verify_payload(example_sso, '')
    assert not base_generator._verify_payload(example_sso + b'abc', example_sig)


def test_prepare_signed_payload(base_generator):
    nonce_dict = {
        b'nonce': b'cb68251eefb5211e58c00ff1395f0c0b'
    }

    payload = base_generator.prepare_signed_payload(nonce_dict)
    assert payload == (
        ('sso', b'bm9uY2U9Y2I2ODI1MWVlZmI1MjExZTU4YzAwZmYxMzk1ZjBjMGI='),
        ('sig', b'1ce1494f94484b6f6a092be9b15ccc1cdafb1f8460a3838fbb0e0883c4390471'),
    )

    # We check that sso parses to expected nonce.
    sso = dict(payload)['sso']
    assert parse_qs(base64.b64decode(sso)) == {
        b'nonce': [b'cb68251eefb5211e58c00ff1395f0c0b']
    }


@pytest.mark.django_db
def test_sso_provider(example_secret, example_producer_url, example_user):

    expected_url = (
        'http://example.org/sso?sso=bm9uY2U9ZWFmMmQ3NDY'
        '3NDk3ZjhiYTM1OGU0NTRhNzkxMWYxNmQmZW1haWw9Zm9vJ'
        'TQwYmFyLnBsJnVzZXJuYW1lPWZvbyZleHRlcm5hbF9pZD0'
        'x&sig=cb690d472636902abd5e43a88db8d502d04dad22'
        '4516d30a90efa74ba4a2ae00'
    )

    service = utils.SSOProviderService(
        sso_key=example_secret,
    )

    response = service.get_signed_url(
        redirect_to=example_producer_url,
        user=example_user,
        sso=unquote(
            'bm9uY2U9ZWFmMmQ3NDY3NDk3ZjhiYTM1OGU0NTRhNzkxMWYxNmQmcmV0dXJ'
            'u%0AX3Nzb191cmw9aHR0cCUzQSUyRiUyRmxvY2FsaG9zdCUzQTgwODElMkZ'
            'zZXNz%0AaW9uJTJGc3NvX2xvZ2lu%0A'
        ),
        signature='cd3181ea14dde017a8980c455c19fd10f679fb1fbd778be7125c7602bb792b12'
    )

    assert response == expected_url


@pytest.mark.django_db
def test_sso_provider_invalid_sig(example_secret, example_producer_url, example_user):

    service = utils.SSOProviderService(
        sso_key=example_secret,
    )

    response = service.get_signed_url(
        redirect_to=example_producer_url,
        user=example_user,
        sso=unquote(
            ''
        ),
        signature='test'
    )

    assert response is None
