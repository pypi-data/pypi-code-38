import logging
from unittest import TestCase
from unittest.mock import patch, MagicMock
from urllib.error import HTTPError
from testfixtures import LogCapture
from bebanjo import things, MovidaAPI
from .utils import create_thingfetcher_instance_from_file

logger = things.logger
logger.setLevel(logging.INFO)

API_URL = 'http://localhost:8080/api'

mapi = MovidaAPI(url=API_URL)
title = create_thingfetcher_instance_from_file(
    baseclass=things.ThingFetcher,
    classname='Title',
    url='http://localhost:8080/api/titles/1001',
    filename='tests/__files/title_1001_exp_m.xml'
)

class TestLog(TestCase):

    def setUp(self):
        patcher = patch('urllib.request.urlopen')
        self.mock_urlopen = patcher.start()
        self.addCleanup(patcher.stop)

    def test_fetch_ok_log(self):
        cm = MagicMock()
        cm.getcode.return_value = 200
        cm.read.return_value = b'<root />'
        self.mock_urlopen.return_value = cm
        with LogCapture() as log:
            mapi.fetch()
        log.check(('bebanjo.things', 'INFO', f'GET {API_URL} returned status 200'),)

    def test_fetch_404_log(self):
        self.mock_urlopen.side_effect = HTTPError(url=None, code=404, msg=None, hdrs=None, fp=None)
        with LogCapture() as log:
            with self.assertRaises(HTTPError):
                mapi.fetch()
        log.check(
            ('bebanjo.things', 'ERROR',
             'GET http://localhost:8080/api returned status 404'),
        )

    def test_raises_create_http_error(self):
        self.mock_urlopen.side_effect = HTTPError(url=None, code=422, msg=None, hdrs=None, fp=None)
        with LogCapture() as log:
            with self.assertRaises(HTTPError):
                mapi.titles.create({'external_id': '172632'})
        log.check(
            ('bebanjo.things', 'ERROR',
             'POST http://localhost:8080/api/titles returned status 422'),
        )

    def test_raises_update_http_error(self):
        self.mock_urlopen.side_effect = HTTPError(url=None, code=422, msg=None, hdrs=None, fp=None)
        with LogCapture() as log:
            with self.assertRaises(HTTPError):
                title.metadata.update({'description': '928329'})
        log.check(
            ('bebanjo.things', 'ERROR',
             'PUT http://localhost:8080/api/titles/1001/metadata returned status 422'),
        )

    def test_raises_delete_http_error(self):
        self.mock_urlopen.side_effect = HTTPError(url=None, code=422, msg=None, hdrs=None, fp=None)
        with LogCapture() as log:
            with self.assertRaises(HTTPError):
                title.delete()
        log.check(
            ('bebanjo.things', 'ERROR',
             'DELETE http://localhost:8080/api/titles/1001 returned status 422'),
        )
