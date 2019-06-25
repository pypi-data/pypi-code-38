import pytest
import responses
from mock import MagicMock
from cipcore import FTPService
from ciperror import FTPServiceRequestError, NotificationError
from hamcrest import assert_that, has_key, has_entry
import json
from pdb import set_trace as bp

DELIVERY_JOB = {"id": "123456789",
                "ladder": "AQ",
                "files": [{
                    "type": "video",
                    "checksum": "4bac27393bdd9777ce02453256c5577cd02275510b2227f473d03f533924f877",
                    "path": "/mnt/elemental/elemental/celula_file_to_vod/output/ingest_teste_AP_90p_103k_x264.mp4",
                    "height": 90,
                    "bitrate": 103000,
                    "codec": "AVC",
                    "step": "delivery-new"
                },
                    {
                        "type": "video",
                        "checksum": "4bac27393bdd9777ce02453256c5577cd02275510b2227f473d03f533924f877",
                        "path": "/mnt/elemental/elemental/celula_file_to_vod/output/ingest_teste_AP_480p_1221k_x264.mp4",
                        "height": 480,
                        "bitrate": 1221000,
                        "codec": "AVC",

                        "step": "delivery-new"
                    }
                ]}

CALLBACK_URL = "http://mamintegrationservice.dev.glb-cip.ninja/api/tasks-response"

SFTP_URI = "sftp://ingest:ingest@192.168.5.8:22"

URL = "http://api.teste.com"

OBJ = MagicMock()

def check_json(json_expected, json_response):
    if type(json_expected) is list:
        for i in range(0, len(json_expected)):
            check_json(json_expected[i], json_response[i])
            check_json(json_response[i], json_expected[i])
    else:
        for key, value in json_expected.items():
            if type(value) is dict:
                assert_that(json_response, has_key(key))
                check_json(value, json_response[key])
                check_json(json_response[key], value)
            elif type(value) is list:
                for i in range(0, len(value)):
                    check_json(json_expected[key][i], json_response[key][i])
                    check_json(json_response[key][i], json_expected[key][i])
            else:
                assert_that(json_response, has_entry(key, value))


@pytest.fixture
def mocked_responses():
    with responses.RequestsMock() as rsps:
        yield rsps


def test_add_ftp_service_base_url():
    ftp_service = FTPService(base_url=URL, sftp_uri=SFTP_URI, logger=OBJ, callback_url=CALLBACK_URL)
    assert(ftp_service.base_url == 'http://api.teste.com/api')


def test_add_ftp_service_sftp_uri():
    ftp_service = FTPService(base_url=URL, sftp_uri=SFTP_URI, logger=OBJ, callback_url=CALLBACK_URL)
    assert(ftp_service.sftp_uri == SFTP_URI)


def test_add_ftp_service_logger_object():
    ftp_service = FTPService(base_url=URL, sftp_uri=SFTP_URI, logger=OBJ, callback_url=CALLBACK_URL)
    assert(ftp_service.logger == OBJ)

def test_add_ftp_service_callback_url():
    ftp_service = FTPService(base_url=URL, sftp_uri=SFTP_URI, logger=OBJ, callback_url=CALLBACK_URL)
    assert (ftp_service.callback_url == CALLBACK_URL)

def test_ftp_service_send_file(mocked_responses):
    response = {
      "callback":"http://mamintegrationservice.dev.glb-cip.ninja/api/tasks-response",
      "body":{
        "id": "123456789",
        "ladder": "AQ",
        "host": "192.168.5.8",
        "port": 22,
        "user": "ingest",
        "password": "ingest",
        "files_to_upload":[
          {
            "in":"/mnt/elemental/elemental/celula_file_to_vod/output/ingest_teste_AP_90p_103k_x264.mp4",
            "out":"ingest_teste_AP_90p_103k_x264.mp4",
            "status":""
          },
          {
            "in":"/mnt/elemental/elemental/celula_file_to_vod/output/ingest_teste_AP_480p_1221k_x264.mp4",
            "out":"ingest_teste_AP_480p_1221k_x264.mp4",
            "status":""
          }
        ]
      }
    }

    ftp_service = FTPService(base_url=URL, sftp_uri=SFTP_URI, logger=OBJ, callback_url=CALLBACK_URL)

    mocked_responses.add(responses.POST, 'http://api.teste.com/api/upload-file', body='', status=200,
                         content_type='application/json')
    resp = ftp_service.send_file(DELIVERY_JOB)
    assert resp.text == ''

    requested = json.loads(mocked_responses.calls._calls[0].request.body.decode(encoding='utf-8', errors='strict'))
    check_json(requested, response)


def test_ftp_service_send_error_wrong_json(mocked_responses):
    ftp_service = FTPService(base_url=URL, sftp_uri=SFTP_URI, logger=OBJ, callback_url=CALLBACK_URL)
    resp = ftp_service.send_file({})
    assert resp == False


def test_ftp_service_healthcheck(mocked_responses):
    ftp_service = FTPService(base_url=URL, sftp_uri=SFTP_URI, logger=OBJ, callback_url=CALLBACK_URL)
    mocked_responses.add(responses.GET, 'http://api.teste.com/api/healthcheck',
                body='', status=200, content_type='application/json')
    resp = ftp_service.healthcheck()
    assert resp == True


def test_send_ftp_service_offline(mocked_responses):
    ftp_service = FTPService(base_url=URL, sftp_uri=SFTP_URI, logger=OBJ, callback_url=CALLBACK_URL)
    try:
        resp = ftp_service.send_file(DELIVERY_JOB)
    except NotificationError as error:
        assert ('Erro no request para o Email Service' in error.message) == 1
        assert ('Connection refused' in error.message) == 1
        a = OBJ.error.call_args_list[0][0]
        # testing if an error log with the right error code is produced
        assert ('GAE0027' in OBJ.error.call_args_list[0][0][0]) == 1


def test_healthcheck_ftp_service_offline(mocked_responses):
    ftp_service = FTPService(base_url=URL, sftp_uri=SFTP_URI, logger=OBJ, callback_url=CALLBACK_URL)
    resp = ftp_service.healthcheck()
    assert resp == False
    assert ('GAE031' in OBJ.error.call_args_list[2][0][0]) == 1

def test_healthcheck_ftp_service_returns_error(mocked_responses):
    body = "{}"
    mocked_responses.add(responses.GET, 'http://api.teste.com/api/healthcheck',
                body=body, status=500, content_type='application/json')
    ftp_service = FTPService(base_url=URL, sftp_uri=SFTP_URI, logger=OBJ, callback_url=CALLBACK_URL)
    resp = ftp_service.healthcheck()
    assert resp == False
    assert ('GAE031' in OBJ.error.call_args_list[2][0][0]) == 1
        

