import datetime
import decimal
import pytest
import six
import time
import uuid

from requests.exceptions import ConnectionError

from msz_svr_conn import ApiConnection

if six.PY3:
    from unittest import mock
else:
    import mock


@pytest.fixture
def args():
    return (
        'test_host/', 'test_oauth_id', 'test_oauth_secret',
        'test_user_email', 'test_user_password'
    )


@pytest.fixture
def base_headers():
    return {
        "Accept": "application/json, */*"
    }


@pytest.fixture
def credz():
    return {
        'access_token': 'test_access_token',
        'token_type': 'Bearer',
        'expires_in': 3600,
        'refresh_token': 'test_refresh_token',
    }


class check_warnings(object):

    def __enter__(self):
        pass

    def __exit__(self):
        pass


def test_construction_no_token_url(args, base_headers):
    conn = ApiConnection(*args)
    assert conn.base_url == "https://test_host/"
    assert conn.base_headers == base_headers


def test_construction_invalid_scheme(args):
    with pytest.raises(AssertionError):
        ApiConnection(*args, scheme='htps')


@mock.patch("msz_svr_conn.ApiConnection.authenticate")
def test_construction_with_token_url(mock_authenticate, args, credz):
    mock_authenticate.return_value = credz
    conn = ApiConnection(*args, token_url='http://authsrv.com/url')

    assert conn.base_url == "https://test_host/"
    mock_authenticate.assert_called_with('http://authsrv.com/url', scopes=None)


@mock.patch('msz_svr_conn.connection.requests')
def test_authenticate_with_init(mock_requests, args, credz):
    mock_response = mock.MagicMock(status_code=200,)
    mock_response.json.return_value = credz
    mock_response.json = mock.MagicMock(return_value=credz)
    mock_requests.request = mock.MagicMock(return_value=mock_response)

    conn = ApiConnection(*args, token_url="http://authsrv.com/")

    test_payload = {
        'client_id': 'test_oauth_id',
        'client_secret': 'test_oauth_secret',
        'username': 'test_user_email',
        'password': 'test_user_password',
        'grant_type': 'password'
    }

    assert conn.credentials == credz
    assert conn.base_headers['Authorization'] == 'Bearer test_access_token'
    mock_requests.request.assert_called_with(
        method='POST', url='http://authsrv.com/', data=test_payload
    )


@mock.patch('msz_svr_conn.connection.requests')
def test_init_maintains_token_url(mock_requests, args, credz):
    mock_response = mock.MagicMock(status_code=200,)
    mock_response.json.return_value = credz
    mock_response.json = mock.MagicMock(return_value=credz)
    mock_requests.request = mock.MagicMock(return_value=mock_response)

    conn = ApiConnection(*args, token_url="http://authsrv.com/")

    test_payload = {
        'client_id': 'test_oauth_id',
        'client_secret': 'test_oauth_secret',
        'username': 'test_user_email',
        'password': 'test_user_password',
        'grant_type': 'password'
    }

    assert conn.credentials == credz
    assert conn.base_headers['Authorization'] == 'Bearer test_access_token'
    mock_requests.request.assert_called_with(
        method='POST', url='http://authsrv.com/', data=test_payload
    )

    mock_requests.reset_mock()
    conn.authenticate()
    mock_requests.request.assert_called_with(
        method='POST', url='http://authsrv.com/', data=test_payload
    )

    mock_requests.reset_mock()
    conn.authenticate(token_url="http://jobs")
    mock_requests.request.assert_called_with(
        method='POST', url="http://jobs", data=test_payload
    )


@mock.patch('msz_svr_conn.connection.requests')
def test_authenticate_with_init_and_scopes(mock_requests, args, credz):
    mock_response = mock.MagicMock(status_code=200,)
    mock_response.json.return_value = credz
    mock_response.json = mock.MagicMock(return_value=credz)
    mock_requests.request = mock.MagicMock(return_value=mock_response)

    conn = ApiConnection(
        *args, token_url="http://authsrv.com/",
        scopes=['claim_read', 'claim_write']
    )

    test_payload = {
        'client_id': 'test_oauth_id',
        'client_secret': 'test_oauth_secret',
        'username': 'test_user_email',
        'password': 'test_user_password',
        'grant_type': 'password',
        'scope': 'claim_read claim_write'
    }

    assert conn.credentials == credz
    assert conn.base_headers['Authorization'] == 'Bearer test_access_token'
    mock_requests.request.assert_called_with(
        method='POST', url='http://authsrv.com/', data=test_payload
    )


@mock.patch('msz_svr_conn.connection.requests')
def test_authenticate(mock_requests, args, credz):
    mock_response = mock.MagicMock(status_code=200,)
    mock_response.json.return_value = credz
    mock_requests.request = mock.MagicMock(return_value=mock_response)

    conn = ApiConnection(*args)
    conn.authenticate("http://authsrv.com/")

    test_payload = {
        'client_id': 'test_oauth_id',
        'client_secret': 'test_oauth_secret',
        'username': 'test_user_email',
        'password': 'test_user_password',
        'grant_type': 'password'
    }

    assert conn.credentials == credz
    assert conn.base_headers['Authorization'] == 'Bearer test_access_token'
    mock_requests.request.assert_called_with(
        method='POST', url='http://authsrv.com/', data=test_payload
    )


@mock.patch('msz_svr_conn.connection.requests')
def test_refresh(mock_requests, args, credz):
    mock_response = mock.MagicMock(status_code=200,)
    mock_response.json.return_value = credz
    mock_requests.request = mock.MagicMock(return_value=mock_response)

    conn = ApiConnection(*args)
    conn.credentials = {
        "refresh_token": "aaa"
    }
    conn.refresh("http://authsrv.com/")

    test_payload = {
        'client_id': 'test_oauth_id',
        'client_secret': 'test_oauth_secret',
        'refresh_token': 'aaa',
        'grant_type': 'refresh_token'
    }

    assert conn.credentials == credz
    assert conn.base_headers['Authorization'] == 'Bearer test_access_token'
    mock_requests.request.assert_called_with(
        method='POST', url='http://authsrv.com/', data=test_payload
    )


@mock.patch('msz_svr_conn.connection.requests')
def test_authenticate_with_scopes(mock_requests, args, credz):
    mock_response = mock.MagicMock(status_code=200,)
    mock_response.json.return_value = credz
    mock_requests.request = mock.MagicMock(return_value=mock_response)

    scopes = ['claim_read', 'claim_write']
    conn = ApiConnection(*args)
    conn.authenticate("http://authsrv.com/", scopes)

    test_payload = {
        'client_id': 'test_oauth_id',
        'client_secret': 'test_oauth_secret',
        'username': 'test_user_email',
        'password': 'test_user_password',
        'grant_type': 'password',
        'scope': " ".join(scopes)
    }

    assert conn.credentials == credz
    assert conn.base_headers['Authorization'] == 'Bearer test_access_token'
    mock_requests.request.assert_called_with(
        method='POST', url='http://authsrv.com/', data=test_payload
    )


@mock.patch('msz_svr_conn.connection.requests')
def test_refresh_with_scopes(mock_requests, args, credz):
    mock_response = mock.MagicMock(status_code=200,)
    mock_response.json.return_value = credz
    mock_requests.request = mock.MagicMock(return_value=mock_response)

    conn = ApiConnection(*args)
    conn.credentials = {
        "refresh_token": "aaa"
    }
    conn.refresh("http://authsrv.com/", scopes=['read', 'write'])

    test_payload = {
        'client_id': 'test_oauth_id',
        'client_secret': 'test_oauth_secret',
        'refresh_token': 'aaa',
        'grant_type': 'refresh_token',
        'scope': 'read write'
    }

    assert conn.credentials == credz
    assert conn.base_headers['Authorization'] == 'Bearer test_access_token'
    mock_requests.request.assert_called_with(
        method='POST', url='http://authsrv.com/', data=test_payload
    )


@mock.patch('msz_svr_conn.connection.requests')
def test_authentication_failure(mock_requests, args):
    mock_response = mock.MagicMock(status_code=403, text='haha..u screwed')
    mock_requests.request = mock.MagicMock(return_value=mock_response)

    with pytest.raises(ApiConnection.AuthFailure) as context:
        ApiConnection(*args, token_url='http://authsrv.com/')

    assert context.value.status_code == 403
    assert context.value.response == "haha..u screwed"


@mock.patch('msz_svr_conn.connection.requests')
def test_refresh_failure(mock_requests, args):
    mock_response = mock.MagicMock(status_code=403, text='haha..u screwed')
    mock_requests.request = mock.MagicMock(return_value=mock_response)

    with pytest.raises(ApiConnection.AuthFailure) as context:
        a = ApiConnection(*args)
        setattr(a, "credentials", {"refresh_token": "ooo"})
        a.refresh('http://domain.com')

    assert context.value.status_code == 403
    assert context.value.response == "haha..u screwed"


def test_refresh_before_authenticate_raises(args):
    a = ApiConnection(*args)

    with pytest.raises(ValueError) as ve:
        a.refresh('http://domain.com')

    assert str(ve.value) == "authenticate not yet called"


@mock.patch('msz_svr_conn.connection.requests')
def test_call_stub(mock_requests, args, base_headers, credz):
    mock_response = mock.MagicMock(status_code=200,)
    mock_response.json.return_value = credz
    mock_requests.request = mock.MagicMock(return_value=mock_response)

    conn = ApiConnection(*args, token_url='http://authsrv.com/')
    assert conn.base_headers['Authorization'] == 'Bearer test_access_token'
    test_results = {'test_data': 'test_json'}
    mock_response.json.return_value = test_results

    test_files = {'file': ('test.csv', 'row,one\nrow,two\n')}
    result = conn.call_stub('test_url/', method='POST', files=test_files)

    assert result == test_results

    test_headers = {
        'Authorization': 'Bearer test_access_token'
    }
    test_headers.update(base_headers)

    mock_requests.request.assert_called_with(
        method='POST', url='https://test_host/test_url/', params=None,
        files=test_files, data=None, headers=test_headers)


@mock.patch('msz_svr_conn.connection.requests')
def test_call_stub_with_non_json_contenttype(
        mock_requests, args, base_headers, credz):
    base_headers['Content-Type'] = 'application/pdf'
    mock_response = mock.MagicMock(status_code=200,)
    mock_response.json.return_value = credz
    mock_requests.request = mock.MagicMock(return_value=mock_response)

    conn = ApiConnection(*args, token_url='http://authsrv.com/')
    assert conn.base_headers['Authorization'] == 'Bearer test_access_token'

    mock_response.json = mock.MagicMock(
        return_value=Exception('Invalid Content-type'))

    # Not implementing this inside a Mock will raise a
    # *** UnicodeEncodeError: 'ascii' codec can't encode character u'\u03c4' in position 0: ordinal not in range(128)  # noqa
    # when you call conn.call_stub below
    # However, you can safely assert that the result is equivalent to
    # `mock_response.content`
    mock_response.content = mock.MagicMock(
        b'\xcf\x84o\xcf\x81\xce\xbdo\xcf\x82'.decode('utf-16'))

    result = conn.call_stub(
        'test_url/something.pdf', method='POST', disable_json_parsing=True)

    assert isinstance(mock_response.json.return_value, Exception)
    assert result == mock_response.content
    assert str(mock_response.json.return_value) == 'Invalid Content-type'


@mock.patch('msz_svr_conn.connection.requests')
def test_call(mock_requests, args, base_headers, credz):
    mock_response = mock.MagicMock(status_code=200,)
    mock_response.json.return_value = credz
    mock_requests.request = mock.MagicMock(return_value=mock_response)

    conn = ApiConnection(*args, token_url='http://authsrv.com/')
    assert conn.base_headers['Authorization'] == 'Bearer test_access_token'
    test_results = {'test_data': 'test_json'}
    mock_response.json.return_value = test_results

    result = conn.call('test_url/', method='POST')

    assert result == test_results

    test_headers = {
        'Authorization': 'Bearer test_access_token'
    }
    test_headers.update(base_headers)

    mock_requests.request.assert_called_with(
        method='POST', url='https://test_host/test_url/', files=None,
        params=None, data=None, headers=test_headers)


@mock.patch('msz_svr_conn.connection.requests')
def test_call_with_payload(mock_requests, args, credz, base_headers):
    mock_response = mock.MagicMock(status_code=200,)
    mock_response.json.return_value = credz
    mock_requests.request = mock.MagicMock(return_value=mock_response)

    conn = ApiConnection(*args, token_url='http://authsrv.com/')
    assert conn.base_headers['Authorization'] == 'Bearer test_access_token'

    test_results = {'test_data': 'test_json'}
    mock_response.json.return_value = test_results

    test_payload = {
        'field': 'value'
    }

    result = conn.call(
        method='POST', url='test_url/', payload=test_payload
    )

    assert result == test_results

    test_headers = {
        'Authorization': 'Bearer test_access_token',
        'Content-Type': 'application/json'
    }
    test_headers.update(base_headers)

    test_json = '{"field": "value"}'

    mock_requests.request.assert_called_with(
        method='POST', url='https://test_host/test_url/', files=None,
        params=None, data=test_json, headers=test_headers)


@mock.patch('msz_svr_conn.connection.requests')
def test_call_with_headers(mock_requests, args, credz, base_headers):
    mock_response = mock.MagicMock(status_code=200,)
    mock_response.json.return_value = credz
    mock_requests.request = mock.MagicMock(return_value=mock_response)

    conn = ApiConnection(*args, token_url='http://authsrv.com/')
    assert conn.base_headers['Authorization'] == 'Bearer test_access_token'
    test_results = {'test_data': 'test_json'}
    mock_response.json.return_value = test_results

    extra_header = {
        'Test-Header': 'test_header_value'
    }

    result = conn.call(
        'test_url/', method='POST', extra_headers=extra_header
    )

    assert result == test_results

    test_headers = {
        'Authorization': 'Bearer test_access_token',
        'Test-Header': 'test_header_value'
    }
    test_headers.update(base_headers)

    mock_requests.request.assert_called_with(
        method='POST', url='https://test_host/test_url/', files=None,
        params=None, data=None, headers=test_headers)


@mock.patch('msz_svr_conn.connection.requests')
def test_call_failure(mock_requests, credz, args):
    mock_response = mock.MagicMock(status_code=200,)
    mock_response.json.return_value = credz
    mock_requests.request = mock.MagicMock(return_value=mock_response)

    conn = ApiConnection(*args, token_url='http://authsrv.com/')
    assert conn.base_headers['Authorization'] == 'Bearer test_access_token'

    mock_response.configure_mock(
        status_code=404, text='kumenuka', request={}
    )
    with pytest.raises(ApiConnection.RequestFailure) as context:
        conn.call('test_url/', method='POST')

    ex = context.value
    assert ex.status_code == 404
    assert ex.method == 'POST'
    assert ex.url == 'https://test_host/test_url/'
    assert ex.response == 'kumenuka'
    assert ex.payload is None
    assert ex.request == {}


@mock.patch('msz_svr_conn.connection.requests')
def test_call_refreshes_on_401(mock_requests, credz, args):
    mock_response = mock.MagicMock(status_code=200,)
    mock_response.json.return_value = credz
    mock_requests.request = mock.MagicMock(return_value=mock_response)

    conn = ApiConnection(*args, token_url='http://authsrv.com/')
    assert conn.base_headers['Authorization'] == 'Bearer test_access_token'
    conn.refresh = mock.MagicMock()

    mock_response.configure_mock(
        status_code=401, text='you shall not pass!', request={}
    )

    with pytest.raises(ApiConnection.RequestFailure) as context:
        conn.call('test_url/', method='POST')
    conn.refresh.assert_called_with()
    ex = context.value
    assert ex.response == 'you shall not pass!'
    assert ex.status_code == 401


@mock.patch('msz_svr_conn.connection.requests')
def test_call_refreshes_on_403(mock_requests, credz, args):
    mock_response = mock.MagicMock(status_code=200,)
    mock_response.json.return_value = credz
    mock_requests.request = mock.MagicMock(return_value=mock_response)

    conn = ApiConnection(*args, token_url='http://authsrv.com/')
    assert conn.base_headers['Authorization'] == 'Bearer test_access_token'
    conn.refresh = mock.MagicMock()

    mock_response.configure_mock(
        status_code=403, text='you shall not pass!', request={}
    )

    with pytest.raises(ApiConnection.RequestFailure) as context:
        conn.call('test_url/', method='POST')
    conn.refresh.assert_called_with()
    ex = context.value
    assert ex.response == 'you shall not pass!'
    assert ex.status_code == 403


@mock.patch('msz_svr_conn.connection.requests')
def test_call_auth_retries(mock_requests, args):
    mock_response = mock.MagicMock(status_code=403)
    mock_requests.request = mock.MagicMock(return_value=mock_response)
    ApiConnection.authenticate = mock.MagicMock()

    conn = ApiConnection(*args, token_url='', auth_retries=5)
    with pytest.raises(ApiConnection.RequestFailure):
        conn.call('test_url/')
    assert conn.authenticate.call_count == 6  # plus the initial authenticate


@mock.patch('msz_svr_conn.connection.requests')
def test_call_auth_retries_none(mock_requests, args):
    mock_response = mock.MagicMock(status_code=403)
    mock_requests.request = mock.MagicMock(return_value=mock_response)
    ApiConnection.authenticate = mock.MagicMock()
    ApiConnection.refresh = mock.MagicMock()

    conn = ApiConnection(*args, token_url='', auth_retries=None)
    with pytest.raises(ApiConnection.RequestFailure):
        conn.call('test_url/')
    assert conn.authenticate.call_count == 1  # the normal flow
    assert conn.refresh.call_count == 0  # refresh won't be called


@mock.patch('msz_svr_conn.connection.requests')
def test_call_auth_retries_delay(mock_requests, args):
    mock_response = mock.MagicMock(status_code=403)
    mock_requests.request = mock.MagicMock(return_value=mock_response)
    ApiConnection.authenticate = mock.MagicMock()

    conn = ApiConnection(
        *args, token_url='', auth_retries=1, auth_retry_delay=1)
    start = time.time()
    with pytest.raises(ApiConnection.RequestFailure):
        conn.call('test_url/')
    duration = time.time() - start
    assert duration > 1
    assert duration < 2


@mock.patch('msz_svr_conn.connection.requests')
def test_call_timeout_retries(mock_requests, args):
    mock_response = mock.MagicMock(status_code=502)
    mock_requests.request = mock.MagicMock(return_value=mock_response)
    ApiConnection.authenticate = mock.MagicMock()

    conn = ApiConnection(*args, token_url='', timeout_retries=5)
    with pytest.raises(ApiConnection.RequestFailure):
        conn.call('test_url/')
    assert mock_requests.request.call_count == 6  # plus the initial request


@mock.patch('msz_svr_conn.connection.requests')
def test_call_timeout_retries_none(mock_requests, args):
    mock_response = mock.MagicMock(status_code=502)
    mock_requests.request = mock.MagicMock(return_value=mock_response)
    ApiConnection.authenticate = mock.MagicMock()

    conn = ApiConnection(*args, token_url='', timeout_retries=None)
    with pytest.raises(ApiConnection.RequestFailure):
        conn.call('test_url/')
    assert mock_requests.request.call_count == 1  # the normal flow


@mock.patch('msz_svr_conn.connection.requests')
def test_call_timeout_retries_infinite(mock_requests, args):
    mock_response = mock.MagicMock(status_code=502)
    count = {'count': 0}

    def fake_requests(*args, **kwargs):
        count['count'] += 1
        if count['count'] == 3:
            fake_error = {
                'method': None,
                'url': None,
                'status_code': None,
                'response': None,
                'payload': None,
                'request': None,
            }
            raise ApiConnection.RequestFailure('', fake_error)
        return mock_response
    mock_requests.request = mock.MagicMock(side_effect=fake_requests)
    ApiConnection.authenticate = mock.MagicMock()

    conn = ApiConnection(*args, token_url='', timeout_retries=-1)
    with pytest.raises(ApiConnection.RequestFailure):
        conn.call('test_url/')
    assert mock_requests.request.call_count == 3


@mock.patch('msz_svr_conn.connection.requests')
def test_call_timeout_retries_delay(mock_requests, args):
    mock_response = mock.MagicMock(status_code=502)
    mock_requests.request = mock.MagicMock(return_value=mock_response)
    ApiConnection.authenticate = mock.MagicMock()

    conn = ApiConnection(
        *args, token_url='', timeout_retries=1, timeout_retry_delay=1)
    start = time.time()
    with pytest.raises(ApiConnection.RequestFailure):
        conn.call('test_url/')
    duration = time.time() - start
    assert duration > 1
    assert duration < 2


@mock.patch('msz_svr_conn.connection.requests')
def test_call_connect_retries(mock_requests, args):
    mock_requests.request = mock.MagicMock(side_effect=ConnectionError)
    ApiConnection.authenticate = mock.MagicMock()

    conn = ApiConnection(*args, token_url='', connect_retries=5)
    with pytest.raises(ConnectionError):
        conn.call('test_url/')
    assert mock_requests.request.call_count == 6  # plus the initial request


@mock.patch('msz_svr_conn.connection.requests')
def test_call_connect_retries_none(mock_requests, args):
    mock_requests.request = mock.MagicMock(side_effect=ConnectionError)
    ApiConnection.authenticate = mock.MagicMock()

    conn = ApiConnection(*args, token_url='', connect_retries=None)
    with pytest.raises(ConnectionError):
        conn.call('test_url/')
    assert conn.authenticate.call_count == 1  # the normal flow


@mock.patch('msz_svr_conn.connection.requests')
def test_call_connect_retries_infinite(mock_requests, args):
    count = {'count': 0}

    def fake_requests(*args, **kwargs):
        count['count'] += 1
        if count['count'] == 3:
            raise Exception()  # to terminate the while loop
        raise ConnectionError()

    mock_requests.request = mock.MagicMock(side_effect=fake_requests)
    ApiConnection.authenticate = mock.MagicMock()

    conn = ApiConnection(*args, token_url='', connect_retries=-1)
    with pytest.raises(Exception):
        conn.call('test_url/')
    assert mock_requests.request.call_count == 3


@mock.patch('msz_svr_conn.connection.requests')
def test_call_connect_retries_delay(mock_requests, args):
    mock_requests.request = mock.MagicMock(side_effect=ConnectionError)
    ApiConnection.authenticate = mock.MagicMock()

    conn = ApiConnection(
        *args, token_url='', connect_retries=1, connect_retry_delay=1)
    start = time.time()
    with pytest.raises(ConnectionError):
        conn.call('test_url/')
    duration = time.time() - start
    assert duration > 1
    assert duration < 2


def assert_dict_against_json(test_dict, test_json):
    test_args = ('', '', '', '', '')
    conn = ApiConnection(*test_args)

    result = conn.serialize_dict_to_json(test_dict)
    assert result == test_json


def test_serialize_dict_to_json():
    test_string = {
        "Name": "John",
    }
    test_json = '{"Name": "John"}'
    assert_dict_against_json(test_string, test_json)

    test_int = {
        "Age": 1,
    }
    test_json = '{"Age": 1}'
    assert_dict_against_json(test_int, test_json)

    test_float = {
        "Cash": 1000.0,
    }
    test_json = '{"Cash": 1000.0}'
    assert_dict_against_json(test_float, test_json)

    now = datetime.datetime.now()
    test_datetime = {
        "DOB": now,
    }
    test_json = '{"DOB": "%s"}' % now.isoformat()
    assert_dict_against_json(test_datetime, test_json)

    test_none = {
        "Murders": None,
    }
    test_json = '{"Murders": null}'
    assert_dict_against_json(test_none, test_json)

    test_list = {
        "Experience": [],
    }
    test_json = '{"Experience": []}'
    assert_dict_against_json(test_list, test_json)

    test_dict = {
        "Measures": {
            "Chest": 34,
        }
    }
    test_json = '{"Measures": {"Chest": 34}}'
    assert_dict_against_json(test_dict, test_json)

    test_truth = {
        "Single?": True
    }
    test_json = '{"Single?": true}'
    assert_dict_against_json(test_truth, test_json)

    test_fallacy = {
        "Kids?": False
    }
    test_json = '{"Kids?": false}'
    assert_dict_against_json(test_fallacy, test_json)

    test_guid = uuid.uuid4()
    test_json = '{"guid": "' + str(test_guid) + '"}'
    test_dict = {"guid": test_guid}
    assert_dict_against_json(test_dict, test_json)

    test_decimal = decimal.Decimal("1.0")
    test_json = '{"decimal": "1.0"}'
    test_dict = {"decimal": test_decimal}
    assert_dict_against_json(test_dict, test_json)

    class NonSerializable(object):
        pass

    test_non_serializable = {
        "obj": NonSerializable()
    }
    with pytest.raises(TypeError):
        # too lazy to create another connection object just to
        # test this
        assert_dict_against_json(test_non_serializable, "")


def test_urljoin():
    urls = [
        (('https://', 'google.com', '', ), 'https://google.com'),
        (('https://mail.some.domain', 'get/', '/mine'),
            'https://mail.some.domain/get/mine'),
        (('https://', '/domain', 'somewhere/'),
            'https://domain/somewhere/'),
        (('/domain', '/somewhere/'), '/domain/somewhere/'),
        (('domain', '/somewhere/'), 'domain/somewhere/'),
        (('/domain', '/somewhere'), '/domain/somewhere'),
        (('domain', '/somewhere'), 'domain/somewhere'),
        (('domain/', '/somewhere'), 'domain/somewhere'),
        (('', 'https://domain', '', None, ), 'https://domain'),
        (('', 'https://domain', '', '/', ), 'https://domain/'),
        (('', 'https://domain', '/', '/', ), 'https://domain/'),
        (('', 'https://domain', '', None, '/'), 'https://domain/'),
        (('', 'https://domain', '/', None, '/'), 'https://domain/'),
        (('', 'https://domain', '/', None, ), 'https://domain/'),
        (('', 'https://domain', '/'), 'https://domain/'),
    ]

    for i in urls:
        assert ApiConnection.urljoin(*i[0]) == i[1]
