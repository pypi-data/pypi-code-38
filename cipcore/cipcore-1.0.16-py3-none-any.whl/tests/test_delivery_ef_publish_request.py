import pytest
import responses
from mock import MagicMock
from cipcore import DeliveryEfPublishRequestApi
from ciperror import PublisherApiRequestError


@pytest.fixture
def mocked_responses():
    with responses.RequestsMock() as rsps:
        yield rsps

def test_add_ef_delivery_base_url():
    url = 'http://api.teste.com'
    obj = MagicMock()
    ef_delivery_api = DeliveryEfPublishRequestApi(base_url=url, logger=obj)
    assert(ef_delivery_api.base_url == 'http://api.teste.com/api')

def test_add_ef_delivery_logger_object():
    url = 'http://api.teste.com'
    obj = MagicMock()
    ef_delivery_api = DeliveryEfPublishRequestApi(base_url=url, logger=obj)
    assert(ef_delivery_api.logger == obj)

def test_ef_delivery_send(mocked_responses):
    url = 'http://api.teste.com'
    obj = MagicMock()
    ef_delivery_api = DeliveryEfPublishRequestApi(base_url=url, logger=obj)
    body = "{ 'teste': 1 }"
    mocked_responses.add(responses.POST, 'http://api.teste.com/api/publish-request',
                body=body, status=200, content_type='application/json')
    resp = ef_delivery_api.send(body)
    assert resp.status_code == 200
    assert resp.text == body
    assert resp.url == ef_delivery_api.base_url + '/publish-request'

def test_ef_delivery_send_error(mocked_responses):
    with pytest.raises(PublisherApiRequestError) as e_info:
        url = 'http://api.teste.com'
        obj = MagicMock()
        ef_delivery_api = DeliveryEfPublishRequestApi(base_url=url, logger=obj)
        mocked_responses.add(responses.POST, 'http://api.teste.com/api/publish-request',
                            body='{"error_code": 404, "message": "error"}', status=404, content_type='application/json')
        resp = ef_delivery_api.send('')

def test_ef_delivery_send(mocked_responses):
    url = 'http://api.teste.com'
    obj = MagicMock()
    ef_delivery_api = DeliveryEfPublishRequestApi(base_url=url, logger=obj)
    body = "{ 'teste': 1 }"
    mocked_responses.add(responses.POST, 'http://api.teste.com/api/publish-raw-file',
                body=body, status=200, content_type='application/json')
    resp = ef_delivery_api.PublishRawFile(body)
    assert resp.status_code == 200
    assert resp.text == body
    assert resp.url == ef_delivery_api.base_url + '/publish-raw-file'

def test_ef_delivery_send_without_body(mocked_responses):
    url = 'http://api.teste.com'
    obj = MagicMock()
    ef_delivery_api = DeliveryEfPublishRequestApi(base_url=url, logger=obj)
    body = None
    mocked_responses.add(responses.POST, 'http://api.teste.com/api/publish-raw-file',
                body=body, status=200, content_type='application/json')
    resp = ef_delivery_api.PublishRawFile(body)
    assert resp.status_code == 200
    assert resp.url == ef_delivery_api.base_url + '/publish-raw-file'

def test_ef_delivery_healthcheck(mocked_responses):
    url = 'http://api.teste.com'
    obj = MagicMock()
    ef_delivery_api = DeliveryEfPublishRequestApi(base_url=url, logger=obj)
    mocked_responses.add(responses.GET, 'http://api.teste.com/api/healthcheck',
                body='', status=200, content_type='application/json')
    resp = ef_delivery_api.healthcheck()
    assert resp == True


def test_send_ef_delivery_service_offline(mocked_responses):
    url = 'http://wrong-ef-delivery-service-url'
    obj = MagicMock()
    ef_delivery_api = DeliveryEfPublishRequestApi(base_url=url, logger=obj)
    try:
        resp = ef_delivery_api.send("")
    except PublisherApiRequestError as error:
        assert ('Erro no request para o PublisherAPI' in error.message) == 1
        assert ('Connection refused' in error.message) == 1
        a = obj.error.call_args_list[0][0]
        # testing if an error log with the right error code is produced
        assert ('GAE013' in obj.error.call_args_list[0][0][0]) == 1

def test_healthcheck_ef_delivery_service_offline(mocked_responses):
    url = 'http://wrong-ef-delivery-service-url'
    obj = MagicMock()
    ef_delivery_api = DeliveryEfPublishRequestApi(base_url=url, logger=obj)
    resp = ef_delivery_api.healthcheck()
    assert resp == False
    assert ('GAE013' in obj.error.call_args_list[0][0][0]) == 1

def test_healthcheck_ef_delivery_service_returns_error(mocked_responses):
    url = 'http://wrong-ef-delivery-service-url'
    obj = MagicMock()
    body = "{}"
    mocked_responses.add(responses.GET, url + '/api/healthcheck',
                body=body, status=500, content_type='application/json')
    ef_delivery_api = DeliveryEfPublishRequestApi(base_url=url, logger=obj)
    resp = ef_delivery_api.healthcheck()
    assert resp == False
    assert ('GAE013' in obj.error.call_args_list[0][0][0]) == 1
        

