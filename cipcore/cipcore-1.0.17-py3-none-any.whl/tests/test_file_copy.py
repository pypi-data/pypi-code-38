import pytest
import responses
from hamcrest import assert_that, has_key, has_entry
from mock import MagicMock
from cipcore import FileCopyApi
from ciperror import FileCopyApiRequestError

COPY_JOB =  {
        "callback": "http://api.teste.com/api/tasks-responses",
        "body": {
            "job_id": "5b91237b405b88b71dfed3eb",
            "step": "copy-file",
            "files_to_copy": [{
                    "in": "./test1.mp4",
                    "out": "./5b91237b405b88b71dfed3eb.mp4",
                    "status": ""
                },
                {
                    "in": "./test2.mp4",
                    "out": "./5ba1bbb00020020000000000.mp4",
                    "status": ""
                }
            ]
        }
    }

@pytest.fixture
def mocked_responses():
    with responses.RequestsMock() as rsps:
        yield rsps

def test_add_file_copy_service_base_url():
    url = "http://api.teste.com"
    obj = MagicMock()

    ftp_service = FileCopyApi(base_url=url, logger=obj)
    assert(ftp_service.base_url == 'http://api.teste.com/api')

def test_add_file_copy_service_logger_object():
    url = "http://api.teste.com"
    obj = MagicMock()

    ftp_service = FileCopyApi(base_url=url, logger=obj)
    assert(ftp_service.logger == obj)

def test_file_copy_service_send_file(mocked_responses):
    url = "http://api.teste.com"
    obj = MagicMock()

    file_copy_service = FileCopyApi(base_url=url, logger=obj)

    mocked_responses.add(responses.POST, f'{url}/api/filecopy', body='', status=200,
                         content_type='application/json')
    resp = file_copy_service.copy_file(COPY_JOB)
    assert resp.text == ''
    assert resp.status_code == 200
    assert resp.url == file_copy_service.base_url + '/filecopy'

def test_file_copy_service_move_file(mocked_responses):
    url = "http://api.teste.com"
    obj = MagicMock()

    file_copy_service = FileCopyApi(base_url=url, logger=obj)

    mocked_responses.add(responses.POST, f'{url}/api/movefile', body='', status=200,
                         content_type='application/json')
    resp = file_copy_service.move_file(COPY_JOB)
    assert resp.text == ''
    assert resp.status_code == 200
    assert resp.url == file_copy_service.base_url + '/movefile'


def test_file_copy_service_error(mocked_responses):
    with pytest.raises(FileCopyApiRequestError) as e_info:
        url = 'http://api.teste.com'
        obj = MagicMock()
        file_copy_service = FileCopyApi(base_url=url, logger=obj)
        mocked_responses.add(responses.POST, f'{url}/api/filecopy',
                             body='{"error_code": 404, "message": "error"}', status=404,
                             content_type='application/json')
        file_copy_service.copy_file(COPY_JOB)

def test_file_move_service_error(mocked_responses):
    with pytest.raises(FileCopyApiRequestError) as e_info:
        url = 'http://api.teste.com'
        obj = MagicMock()
        file_copy_service = FileCopyApi(base_url=url, logger=obj)
        mocked_responses.add(responses.POST, f'{url}/api/movefile',
                             body='{"error_code": 404, "message": "error"}', status=404,
                             content_type='application/json')
        file_copy_service.move_file(COPY_JOB)

def test_file_copy_healthcheck(mocked_responses):
    url = 'http://api.teste.com'
    obj = MagicMock()
    file_copy_service = FileCopyApi(base_url=url, logger=obj)
    mocked_responses.add(responses.GET, f'{url}/api/healthcheck',
                         body='', status=200, content_type='application/json')
    resp = file_copy_service.healthcheck()
    assert resp == True


def test_file_copy_service_offline(mocked_responses):
    url = 'http://wrong-file_copy-service-url'
    obj = MagicMock()
    file_copy_service = FileCopyApi(base_url=url, logger=obj)
    try:
        file_copy_service.copy_file(COPY_JOB)
    except FileCopyApiRequestError as error:
        assert ('Erro no request para a File Copy API' in error.message) == 1
        assert ('Connection refused' in error.message) == 1


def test_healthcheck_file_copy_service_offline(mocked_responses):
    url = 'http://wrong-ef-delivery-service-url'
    obj = MagicMock()
    file_copy_service = FileCopyApi(base_url=url, logger=obj)
    resp = file_copy_service.healthcheck()
    assert resp == False
    assert ('GAE0020' in obj.error.call_args_list[0][0][0]) == 1
#
#
def test_healthcheck_ef_delivery_service_returns_error(mocked_responses):
    url = 'http://wrong-ef-delivery-service-url'
    obj = MagicMock()
    mocked_responses.add(responses.GET, f'{url}/api/healthcheck',
                         body='{}', status=500, content_type='application/json')
    file_copy_service = FileCopyApi(base_url=url, logger=obj)
    resp = file_copy_service.healthcheck()
    assert resp == False
    assert ('GAE0020' in obj.error.call_args_list[0][0][0]) == 1

