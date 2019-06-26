import sys
import os
import argparse
import signal
import unittest
import flask
import multiprocessing
import time
import requests
import logging

import unittest
from sqlalchemy import text


#we import the different models
from algonaut.settings import settings as settings
from algonaut.api.app import get_app
from algonaut.cli.db import _migrate_db, _clean_db

class DatabaseTest(unittest.TestCase):

    fixtures = []

    @classmethod
    def setup(cls):
        return False

    @classmethod
    def teardown(cls):
        pass

    @classmethod
    def initialize_fixtures(cls):
        _clean_db(settings, None)
        fixture_objs = {}
        for fixture_dict in cls.fixtures:
            for key,fixture in fixture_dict.items():
                objs = fixture(cls, fixture_objs)
                fixture_objs[key] = objs
                setattr(cls, key, objs)

    def setUp(self):

        if not settings.get('test'):
            raise AttributeError("You try to run tests in a non-TEST environment!")

        self.session.rollback()
        self.initialize_fixtures()

    @classmethod
    def tearDownClass(cls):
        cls.teardown()

    @classmethod
    def setUpClass(cls):

        cls.engine = settings.get_db_engine()
        cls.session = settings.get_session(fresh=True)

        _migrate_db(None, None)


class ApplicationProcess(multiprocessing.Process):

    def __init__(self, host, port, app, settings, queue=None):
        super(ApplicationProcess,self).__init__()
        self.host = host
        self.port = port
        self.app = app
        self.queue = queue

    def run(self):

        settings.setup_logging(4)

        application = flask.Flask(__name__)
        application.wsgi_app = self.app

        settings.sessionmaker = None
        settings.test_queue = self.queue
        settings.dispose_all_sessions()


        try:
            application.run(
                debug=True,
                host=self.host,
                port=self.port,
                processes=1,
                use_reloader=False
            )
        except KeyboardInterrupt:
            print("Exiting...")

class ApiTest(DatabaseTest):

    """
    """

    host = 'localhost'
    port = 5557
    protocol = 'http'

    fixtures = []
    settings = None
    app = None
    client = None

    api_base_url = ''
    api_version = 'v1'

    def url(self, name):
        return '{}://{}:{}{}/{}{}'.format(self.protocol, self.host, self.port, self.api_base_url, self.api_version, name)

    def setUp(self):
        super(ApiTest, self).setUp()

    @classmethod
    def tearDownClass(self):
        self.api_process.terminate()
        super(ApiTest, self).tearDownClass()

    @classmethod
    def setUpClass(self):

        super(ApiTest, self).setUpClass()

        #we initialize the settings...
        settings.set('url', '{}://{}:{}{}'.format(self.protocol, self.host, self.port, self.api_base_url))
        settings.initialize()

        if not settings.get('test'):
            raise AttributeError("You try to run tests in a non-test environment!")

        self.test_queue = multiprocessing.Queue()
        self.api_process = ApplicationProcess(self.host,self.port, get_app(settings), settings, queue=self.test_queue)
        self.api_process.start()

        self.settings = settings
        self.app = get_app(settings)
        self.client = self.app.test_client()

        #this parameter might need some tuning to be sure the API is up when the tests start
        time.sleep(0.3)


    def _authenticated_request(self, user, func, url, access_token=None, *args, **kwargs):
        if access_token is None:
            access_token = user.access_token
        headers = {
            'X-Authorization' : 'bearer {}'.format(access_token.token)
        }
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])
            del kwargs['headers']
        return func(self.url(url), *args, headers = headers, **kwargs)

    def authenticated_get(self, user, url, access_token=None, *args, **kwargs):
        return self._authenticated_request(user, requests.get, url, access_token=None, *args, **kwargs)

    def authenticated_post(self, user, url, access_token=None, *args, **kwargs):
        return self._authenticated_request(user, requests.post, url, access_token=None, *args, **kwargs)

    def authenticated_delete(self, user, url, access_token=None, *args, **kwargs):
        return self._authenticated_request(user, requests.delete, url, access_token=None, *args, **kwargs)

    def authenticated_put(self, user, url, access_token=None, *args, **kwargs):
        return self._authenticated_request(user, requests.put, url, access_token=None, *args, **kwargs)

    def authenticated_patch(self, user, url, access_token=None, *args, **kwargs):
        return self._authenticated_request(user, requests.patch, url, access_token=None, *args, **kwargs)
