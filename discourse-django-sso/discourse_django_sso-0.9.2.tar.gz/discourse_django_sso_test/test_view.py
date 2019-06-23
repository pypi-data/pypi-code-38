# coding=utf-8

"""Test sso view."""

import base64
import hashlib
import hmac
from urllib.parse import urlencode, parse_qs

import pytest
from django.contrib.auth.models import User
from django.test import RequestFactory
from django.test.client import Client
from django.urls.base import reverse
from django.utils.encoding import force_bytes

from discourse_django_sso.views import SSOProviderView
from discourse_django_sso_test_project import settings, urls


# pylint: disable=missing-docstring,redefined-outer-name,invalid-name


@pytest.fixture()
def nonce():
    return "random_nonce"


@pytest.fixture()
def sso_key():
    return force_bytes(settings.DISCOURSE_SSO_KEY)


@pytest.fixture()
def sso_contents(nonce, sso_key):
    sso = base64.b64encode(urlencode({'nonce': nonce}).encode('ascii')) + b'\n'
    sig = force_bytes(hmac.new(sso_key, force_bytes(sso), digestmod=hashlib.sha256).hexdigest())
    return {
        "sig": sig,
        "sso": sso
    }


def test_view(admin_client: Client, sso_contents):
    response = admin_client.get(reverse('sso'), data=sso_contents)
    assert response.status_code == 302
    expected_response = (
        "http://localhost/test?"
        "sso=bm9uY2U9cmFuZG9tX25vbmNlJmVtYWlsPWFkbWluJTQwZXhhbXBsZS5jb20mdXNlcm5hbWU9YWRtaW4mZXh0Z"
        "XJuYWxfaWQ9MQ%3D%3D&"
        "sig=8fdf24135101a0e9c360a93ca8c455c666e81bd3b4468aa9d06e1da652cb328a"
    )
    assert response.url == expected_response


def test_view_empty_get(admin_client: Client):
    response = admin_client.get(reverse('sso'), data={})
    assert response.status_code == 400


def test_invalid_data(admin_client: Client):
    response = admin_client.get(reverse('sso'), data={
        "sso": "bm9uY2U9Y2I2ODI1MWVlZmI1MjExZTU4YzAwZmYxMzk1ZjBjMGI=\n",
        "sig": "invalid_sig"
    })
    assert response.status_code == 400


def test_view_no_newline(admin_client: Client):
    response = admin_client.get(reverse('sso'), data={
        "sso": "bm9uY2U9Y2I2ODI1MWVlZmI1MjExZTU4YzAwZmYxMzk1ZjBjMGI=",
        "sig": "invalid_sig"
    })
    assert response.status_code == 400


@pytest.mark.django_db()    # db mark is needed for session
def test_client_url_generaion(client: Client):
    response = client.get(reverse('client'), data={})
    assert response.status_code == 302
    expected_response = (
        "http://www.olcms.org/sso?"
        "sso=bm9uY2U9ZTE1OTE3ZTAzMjA5OTI1OTZmNjM4ZWJmZjc2NzgyMDI%3D&"
        "sig=b7e36a9804e525d398d110fac60e3eba7c5f3d115551a261b9468581fa7cbe35"
    )
    assert response.url == expected_response


@pytest.mark.django_db()
def test_required_args_for_session_gen(client: Client):
    """
    Check that sig and sso are required parameters.
    :param admin_client:
    :return:
    """
    response = client.get(reverse('createSession'), data={})
    assert response.status_code == 400
    response = client.get(reverse('createSession'), data={"sso": "does not matter"})
    assert response.status_code == 400


@pytest.mark.django_db()
def test_error_sso_not_match_sig(client: Client):
    """
    Check that when sso does not match sig error is returned
    :param admin_client:
    :return:
    """
    response = client.get(reverse('createSession'),
                          data={"sso": "does not match", "sig": "not matching"})
    assert response.status_code == 400

# uncomment below lines to generate sso and sig for data that you need for test
# def generate_sig(admin_client: Client):
#  util = SSOClientUtils(sso_key(), 'http://base.url/')  # pylint: disable=wrong-spelling-in-comment
#     payload = [
#         ('nonce', "e15917e0320992596f638ebff7678202"),
#         ('name', "sam"),      # pylint: disable=wrong-spelling-in-comment
#         ('username', "samsam"),   # pylint: disable=wrong-spelling-in-comment
#         ('email', "test@www.pll"),
#         ('external_id', "external_sam"),
#         ('require_activation', "false"),
#     ]
#     signed_stuff = util.prepare_signed_payload(payload)
#     url = util.create_url('http://base.url/', signed_stuff)
#     print(url)
#     assert url is None


@pytest.mark.django_db()
def test_error_invalid_nonce(client: Client):
    try:
        urls.nonce_service.invalidate_nonce(urls.nonce_service.fixed_nonce_val())

        response = client.get(reverse('createSession'), data={
            "sso": 'bm9uY2U9ZTE1OTE3ZTAzMjA5OTI1OTZmNjM4ZWJmZjc2NzgyMDImbmFtZT1zYW0mdXNlcm5hbWU9c2'
                   'Ftc2FtJmVtYWlsPXRlc3QlNDB3d3cucGxsJmV4dGVybmFsX2lkPWV4dGVybmFsX3NhbSZyZXF1aXJl'
                   'X2FjdGl2YXRpb249ZmFsc2U=',
            "sig": 'a12def3d4e056395742b1f15bee99c52d430f9d868b72c511df8c0f082d9f28e'})
        assert response.status_code == 400
    finally:
        urls.nonce_service.clear_invalid_nonces()


@pytest.mark.django_db()
def test_session_generation(client: Client):
    response = client.get(reverse('createSession'), data={
        "sso": 'bm9uY2U9ZTE1OTE3ZTAzMjA5OTI1OTZmNjM4ZWJmZjc2NzgyMDImbmFtZT1zYW0mdXNlcm5hbWU9c2Ftc2F'
               'tJmVtYWlsPXRlc3QlNDB3d3cucGxsJmV4dGVybmFsX2lkPWV4dGVybmFsX3NhbSZyZXF1aXJlX2FjdGl2YX'
               'Rpb249ZmFsc2U=',
        "sig": 'a12def3d4e056395742b1f15bee99c52d430f9d868b72c511df8c0f082d9f28e'})
    assert response.status_code == 302


def test_canned_discourse_respone(rf: RequestFactory):
    real_qs = (
        b'sso=bm9uY2U9ZjVhMmZiMmY0MjhiYTg1ODgwZGY0MWFiNzM0MDdmMzEmcmV0dXJ'
        b'uX3Nzb191cmw9aHR0cCUzQSUyRiUyRmRpc2NvdXJzZS5vbGNtcy5kZXYubG9jYW'
        b'wlM0E4MDgxJTJGc2Vzc2lvbiUyRnNzb19sb2dpbg%3D%3D&sig=074573798234'
        b'a2cc87affbf0b4280031ce3ceb1df681c6a8c2a81e4f5b28ff9e'
    )
    view = SSOProviderView.as_view(
        sso_redirect=settings.DISCOURSE_SSO_REDIRECT,
        sso_secret="qwertyuiopasdfghjklzxcvbnm0987654321"
    )
    request = rf.get('/sso', data=parse_qs(real_qs))
    request.user = User()
    response = view(request)

    assert response.status_code == 302
