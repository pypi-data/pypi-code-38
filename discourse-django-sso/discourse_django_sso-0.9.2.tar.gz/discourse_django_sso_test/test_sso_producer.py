# coding=utf-8
"""Test SSO producer utils."""
import base64

import pytest

from discourse_django_sso.utils import SSOProducerUtils

# pylint: disable=missing-docstring,redefined-outer-name


@pytest.fixture()
def sso_producer(
        example_user,
        example_secret,
        example_producer_url,
        example_sig,
        example_sso
):
    return SSOProducerUtils(
        sso_key=example_secret,
        consumer_url=example_producer_url,
        user=example_user,
        sso=example_sso,
        sig=example_sig
    )


def test_verify_signature(sso_producer):
    assert sso_producer.verify_signature()


def test_get_nonce(sso_producer):
    assert sso_producer.get_nonce() == b'cb68251eefb5211e58c00ff1395f0c0b'


def test_get_response_params(sso_producer, example_user):
    assert sso_producer.get_response_params() == (
        ('nonce', b'cb68251eefb5211e58c00ff1395f0c0b'),
        ('email', example_user.email),
        ('username', example_user.username),
        ('external_id', example_user.id),
    )


def test_get_signed_payload(sso_producer):
    assert sso_producer.get_signed_payload() == (
        ('sso', b'bm9uY2U9Y2I2ODI1MWVlZmI1MjExZTU4YzAwZmYxMzk1ZjBjMGImZW1haWw9Zm9vJTQw'
                b'YmFyLnBsJnVzZXJuYW1lPWZvbyZleHRlcm5hbF9pZD0x'),
        ('sig', b'30cadd6c051e07900ffc27323354f90d03abcee835b55f458de33a51d5dd3341'),
    )


def test_get_sso_redirect(sso_producer):
    expected = 'http://example.org/sso?sig=foo&sso=bar'
    actual = sso_producer.get_sso_redirect((
        ('sig', 'foo'),
        ('sso', 'bar'),
    ))
    assert expected == actual


def test_validate_nonce(sso_producer):
    sso_producer.sso = base64.b64encode(b"something_else=231")
    with pytest.raises(ValueError):
        sso_producer.validate()


