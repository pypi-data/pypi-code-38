import time

import jwt
import pytest
from webtest import TestApp, AppError

from test.conftest import app


@pytest.fixture(scope='function')
def api_client():
    client = TestApp(app)
    yield client


def build_jwt_token(**kwargs):
    return jwt.encode(
        {
            'user': 'test',
            'iss': 'MyTest-test',
            **kwargs,
        },
        key='123', algorithm='HS256'
    ).decode()


@pytest.fixture(scope='function')
def jwt_token():
    return build_jwt_token()


def test_json_response(api_client):
    result = api_client.get('/index')
    assert result.status_int == 200


def test_cors_response(api_client):
    result = api_client.get('/documents')
    print(result._headers)
    assert result.status_int == 200


def test_jwt_authentication_ok(api_client, jwt_token):
    result = api_client.get('/auth_access', headers={'authorization': f"bearer {jwt_token}"})
    assert result.status_int == 200
    assert result.text == 'OK'


def test_jwt_authentication_expired(api_client):
    token = build_jwt_token(exp=int(time.time()))
    with pytest.raises(AppError) as e:
        api_client.get('/auth_access', headers={'authorization': f"bearer {token}"})
    assert '401 Unauthorized' in str(e)


def test_jwt_authentication_wrong_issuer_fail(api_client):
    token = build_jwt_token(iss='MyTest-wrongenv')
    with pytest.raises(AppError) as e:
        api_client.get('/auth_access', headers={'authorization': f"bearer {token}"})
    assert '401 Unauthorized' in str(e)


def test_jwt_authentication_fail(api_client):
    with pytest.raises(AppError) as e:
        api_client.get('/auth_access')
    assert '401 Unauthorized' in str(e)
