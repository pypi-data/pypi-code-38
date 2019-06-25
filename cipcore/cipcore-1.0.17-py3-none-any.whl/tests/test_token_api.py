import pytest
import responses
from mock import MagicMock
from cipcore import TokenApi
from ciperror import ClientCredentialsTokenError
from unittest import mock
import requests

@pytest.fixture
def mocked_responses():
    with responses.RequestsMock() as rsps:
        yield rsps


def test_token_variables():
    obj = MagicMock()
    client_id = '1234'
    secret = '4321'
    token = TokenApi(logger=obj, client_id=client_id, secret=secret)
    assert (token.url == 'https://accounts.backstage.globoi.com/token')
    assert (token.client_id == '1234')
    assert (token.secret == '4321')

def test_encode_method():
    obj = MagicMock()
    client_id = '1234'
    secret = '4321'
    token = TokenApi(logger=obj, client_id=client_id, secret=secret)
    encode = token.encode()
    assert encode == 'MTIzNDo0MzIx'

def test_token_request(mocked_responses):
    obj = MagicMock()
    client_id = '1234'
    secret = '4321'
    token = TokenApi(logger=obj, client_id=client_id, secret=secret)
    body = '{"access_token": "hash", "expires_in": 899, "token_type": "bearer"}'
    mocked_responses.add(responses.POST, 'https://accounts.backstage.globoi.com/token',
                body=body, status=200, content_type='application/x-www-form-urlencoded')
    resp = token.request_token()
    assert resp == 'hash'

def test_token_request_error(mocked_responses):
    with pytest.raises(ClientCredentialsTokenError):
        obj = MagicMock()
        client_id = '1234'
        secret = '4321'
        token = TokenApi(logger=obj, client_id=client_id, secret=secret)
        mocked_responses.add(responses.POST, 'https://accounts.backstage.globoi.com/token',
                            body='{"error_code": 404, "message": "error"}', status=403, content_type='application/json')
        token.request_token()

@mock.patch('requests.post')
def test_token_unexpected_error(mock_request):
    with pytest.raises(ClientCredentialsTokenError):
        obj = MagicMock()
        client_id = '1234'
        secret = '4321'
        token = TokenApi(logger=obj, client_id=client_id, secret=secret)
        mock_request.side_effect = requests.exceptions.ConnectionError()

        with pytest.raises(Exception):
            token.request_token()