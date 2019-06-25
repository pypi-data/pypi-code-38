import pytest
import responses
from mock import MagicMock
from cipcore import EmailApi
from ciperror import EmailServiceRequestError

@pytest.fixture
def mocked_responses():
    with responses.RequestsMock() as rsps:
        yield rsps

def test_add_email_base_url():
    url = 'http://api.teste.com'
    obj = MagicMock()
    email = EmailApi(base_url=url, logger=obj)
    assert(email.base_url == 'http://api.teste.com/api')

def test_add_email_logger_object():
    url = 'http://api.teste.com'
    obj = MagicMock()
    email = EmailApi(base_url=url, logger=obj)
    assert(email.logger == obj)

def test_email_send(mocked_responses):
    url = 'http://api.teste.com'
    obj = MagicMock()
    email = EmailApi(base_url=url, logger=obj)
    body = "{ 'teste': 1 }"
    mocked_responses.add(responses.POST, 'http://api.teste.com/api/email',
                body=body, status=200, content_type='application/json')
    resp = email.send(body)
    assert resp.status_code == 200
    assert resp.text == body
    assert resp.url == email.base_url + '/email'

def test_email_send_error(mocked_responses):
    with pytest.raises(EmailServiceRequestError) as e_info:
        url = 'http://api.teste.com'
        obj = MagicMock()
        email = EmailApi(base_url=url, logger=obj)
        mocked_responses.add(responses.POST, 'http://api.teste.com/api/email',
                            body='{"error_code": 404, "message": "error"}', status=404, content_type='application/json')
        resp = email.send('')

def test_email_healthcheck(mocked_responses):
    url = 'http://api.teste.com'
    obj = MagicMock()
    email = EmailApi(base_url=url, logger=obj)
    mocked_responses.add(responses.GET, 'http://api.teste.com/api/healthcheck',
                body='', status=200, content_type='application/json')
    resp = email.healthcheck()
    assert resp == True


def test_send_email_service_offline(mocked_responses):
    url = 'http://wrong-email-service-url'
    obj = MagicMock()
    email = EmailApi(base_url=url, logger=obj)
    try:
        resp = email.send("")
    except EmailServiceRequestError as error:
        assert ('Erro no request para o Email Service' in error.message) == 1
        assert ('Connection refused' in error.message) == 1
        a = obj.error.call_args_list[0][0]
        # testing if an error log with the right error code is produced
        assert ('GAE0027' in obj.error.call_args_list[0][0][0]) == 1

def test_healthcheck_email_service_offline(mocked_responses):
    url = 'http://wrong-email-service-url'
    obj = MagicMock()
    email = EmailApi(base_url=url, logger=obj)
    resp = email.healthcheck()
    assert resp == False
    assert ('GAE0027' in obj.error.call_args_list[0][0][0]) == 1

def test_healthcheck_email_service_returns_error(mocked_responses):
    url = 'http://wrong-email-service-url'
    obj = MagicMock()
    body = "{}"
    mocked_responses.add(responses.GET, 'http://wrong-email-service-url/api/healthcheck',
                body=body, status=500, content_type='application/json')
    email = EmailApi(base_url=url, logger=obj)
    resp = email.healthcheck()
    assert resp == False
    assert ('GAE0027' in obj.error.call_args_list[0][0][0]) == 1
        

