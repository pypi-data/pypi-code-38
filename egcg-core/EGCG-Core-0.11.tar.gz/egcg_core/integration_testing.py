import json
import requests
from os import getenv
from time import sleep
from datetime import datetime
from unittest import TestCase
from multiprocessing import Lock
from subprocess import check_output
from egcg_core import config, rest_communication


def get_cfg():
    cfg = config.Configuration()
    cfg_file = getenv('INTEGRATIONCONFIG')
    if cfg_file:
        cfg.load_config_file(cfg_file)

    return cfg


def now():
    return datetime.utcnow().strftime('%Y-%m-%d_%H:%M:%S')


class WrappedFunc:
    """For wrapping unittest.TestCase's assert methods, logging details of the assertion carried out."""
    def __init__(self, test_case, assert_func):
        self.test_case = test_case
        self.assert_func = assert_func
        self.lock = Lock()

    def __call__(self, check_name, *args, **kwargs):
        if not isinstance(check_name, str):
            raise NameError('Incorrect call - check_name required')

        assertion_report = '%s.%s\t%s\t%s\t' % (
            self.test_case.__class__.__name__,
            self.test_case._testMethodName,
            check_name,
            self.assert_func.__name__
        )
        args_used = '\t' + str(args)
        if kwargs:
            args_used += ' ' + str(kwargs)

        try:
            self.assert_func(*args, **kwargs)
            self.log(assertion_report + 'success' + args_used)
        except AssertionError:
            self.log(assertion_report + 'failed' + args_used)
            raise

    def log(self, msg):
        with self.lock:
            with open('checks.log', 'a') as f:
                f.write(msg + '\n')


class IntegrationTest(TestCase):
    """Contains some common functionality for patching, and quality-oriented assertion logging."""
    _wrapped_func_blacklist = ('assertRaises', 'assertWarns', 'assertLogs', 'assertRaisesRegex', 'assertWarnsRegex')
    patches = ()

    def __init__(self, *args):
        super().__init__(*args)

        # need separate TestCase with non-wrapped assert methods, because some of them call each other
        self.asserter = TestCase()
        for attrname in dir(self.asserter):
            if attrname.startswith('assert'):
                attr = getattr(self.asserter, attrname)
                if callable(attr) and attrname not in self._wrapped_func_blacklist:
                    setattr(self, attrname, WrappedFunc(self, attr))

        self.cfg = get_cfg()

    def setUp(self):
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in self.patches:
            p.stop()


class ReportingAppIntegrationTest(IntegrationTest):
    """
    Sets up a Reporting-App Docker image before each test, and stops/removes it after. Captures the image's IP address
    and uses that to patch egcg_core.rest_communication.default.
    """
    container_id = None
    container_ip = None
    container_port = None

    def setUp(self):
        super().setUp()

        self.container_id = check_output(
            ['docker', 'run', '-d', self.cfg['reporting_app']['image_name'],
             self.cfg.query('reporting_app', 'branch', ret_default='master')]
        ).decode().strip()
        assert self.container_id

        container_basename = self.cfg.query('reporting_app', 'container_basename')
        if container_basename:
            check_output(['docker', 'rename', self.container_id, container_basename + '_' + self.container_id[:12]])

        container_info = json.loads(check_output(['docker', 'inspect', self.container_id]).decode())[0]
        # for now, assume the container is running on the main 'bridge' network
        self.container_ip = container_info['NetworkSettings']['Networks']['bridge']['IPAddress']
        self.container_port = list(container_info['Config']['ExposedPorts'])[0].rstrip('/tcp')
        container_url = 'http://' + self.container_ip + ':' + self.container_port + '/api/0.1'
        rest_communication.default._baseurl = container_url
        rest_communication.default._auth = (self.cfg['reporting_app']['username'], self.cfg['reporting_app']['password'])
        self._ping(container_url)

    def tearDown(self):
        super().tearDown()

        assert self.container_id
        check_output(['docker', 'stop', self.container_id])
        check_output(['docker', 'rm', '-v', self.container_id])
        self.container_id = self.container_ip = self.container_port = None

    def _ping(self, url, retries=36):
        try:
            requests.get(url, timeout=2)
            return True
        except requests.exceptions.ConnectionError:
            if retries > 0:
                sleep(5)
                return self._ping(url, retries - 1)
            else:
                raise
