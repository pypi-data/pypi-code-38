import unittest
import requests_mock
import requests
import datetime
import hemApp
def test_check_init():
    test = {'path':'/', 'secure':True, 'verify':True}
    check = hemApp.Check('test', test)
    assert check.url == 'https://{}/'
    assert check.verify == True

def test_config_load():
    conf = hemApp.load_config('tests/test_cli.yaml')
    assert 'settings' in conf
    assert 'discovery' in conf

def test_dict_list():
    with requests_mock.mock() as m:
        m.get('https://1.1.1.1/', text="")
        test = {'path':'/', 'secure':True, 'verify':True}
        check = hemApp.Check('test', test)
        results = check.test_list([{"host":"1.1.1.1","name":"ones"}])
        (response, timing) = results[0]
        assert results is not None
        assert response == 200
        assert type(timing) is datetime.timedelta

def test_check_invoke():
    with requests_mock.mock() as m:
        m.get('https://1.1.1.1/', text="")
        test = {'path':'/', 'secure':True, 'verify':True}
        check = hemApp.Check('test', test)
        results = check.test_list(["1.1.1.1"])
        (response, timing) = results[0]
        assert results is not None
        assert response == 200
        assert type(timing) is datetime.timedelta
def test_check_mtls_invoke():
    with requests_mock.mock() as m:
        m.get('https://1.1.1.1/', text="")
        test = {'path':'/', 'secure':True, 'verify':True, 'certificate': 'certificate.pem'}
        check = hemApp.Check('test', test)
        results = check.test_list(["1.1.1.1"])
        (response, timing) = results[0]
        assert results is not None
        assert response == 200
        assert type(timing) is datetime.timedelta
def test_check_jwt_invoke():
    hemstore = hemApp.HemStore()
    with requests_mock.mock() as m:
        m.get('https://1.1.1.1/', text="")
        m.post('https://1.1.1.1/jwt', text='{"jwt":"token"}')
        test = {'path':'/', 'secure':True, 'verify':True, 'auth': {'type':'jwt', 'url':'https://1.1.1.1/jwt', 'field':'jwt'}}
        check = hemApp.Check('test', test, storage=hemstore)
        results = check.test_list(["1.1.1.1"])
        (response, timing) = results[0]
        assert results is not None
        assert response == 200
        assert type(timing) is datetime.timedelta
def test_ssl_error():
    with requests_mock.mock() as m:
        m.get('https://1.1.1.1/', exc=requests.exceptions.SSLError)
        test = {'path':'/', 'secure':True, 'verify':True}
        check = hemApp.Check('test', test)
        results = check.test_list(["1.1.1.1"])
        (response, timing) = results[0]
        assert results is not None
        assert response == 526
        assert type(timing) is datetime.timedelta
def test_connection_timeout():
    with requests_mock.mock() as m:
        m.get('https://1.1.1.1/', exc=requests.exceptions.ConnectTimeout)
        test = {'path':'/', 'secure':True, 'verify':True}
        check = hemApp.Check('test', test)
        results = check.test_list(["1.1.1.1"])
        (response, timing) = results[0]
        assert results is not None
        assert response == 522
        assert type(timing) is datetime.timedelta

def test_check_headers():
    import hemApp
    with requests_mock.mock() as m:
        m.get('https://1.1.1.1/', text="",  request_headers={"host": "example.com"})
        test = {'path':'/', 'secure':True, 'verify':True, "headers":{"host":"example.com"}}
        check = hemApp.Check('test', test)
        results = check.test_list(["1.1.1.1"])
        (response, timing) = results[0]
        assert results is not None
        assert response == 200
        assert type(timing) is datetime.timedelta
        test = {'path':'/', 'secure':True, 'verify':True, "headers":{"host":"notexample.com"}}
        check = hemApp.Check('test', test)
        try:
            results = check.test_list(["1.1.1.1"])
            assert results == []
        except requests_mock.exceptions.NoMockAddress as m:
            exit(m)
            assert "host test" is "host test"
