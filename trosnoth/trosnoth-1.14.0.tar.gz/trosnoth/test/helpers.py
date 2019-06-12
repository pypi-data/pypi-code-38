import logging
import io
import sys

import pytest


def sendMessage(plug, msg):
    plug._receive(msg)


@pytest.fixture(name='logman')
def fixture_logman(request):
    '''
    Defines a log manager py.test funcarg which redirects logs to stdout and
    allows assertions about whether errors were recorded in the logs.
    '''
    logman = LogManager()
    request.addfinalizer(logman.teardown)
    return logman


class LogManager(object):
    def __init__(self):
        self.stdout_log_handler = logging.StreamHandler(sys.stdout)
        self.stdout_log_handler.setFormatter(logging.Formatter('%(levelname)s:%(name)s: %(message)s'))
        self.error_buffer = io.StringIO()
        self.error_log_handler = logging.StreamHandler(self.error_buffer)
        self.expect_no_errors = True

        self.stdout_log_handler.setLevel(logging.DEBUG)
        logging.getLogger().addHandler(self.stdout_log_handler)
        self.error_log_handler.setLevel(logging.ERROR)
        logging.getLogger().addHandler(self.error_log_handler)

        logging.getLogger().setLevel(logging.DEBUG)

    def ignore_errors(self):
        '''
        Call this method to instruct the log manager to ignore ERROR or CRITICAL
        log messages. Note that if you have already called assert_errors() or
        assert_no_errors(), you do not need to call ignore_errors().
        '''
        self.expect_no_errors = False

    def teardown(self):
        logging.getLogger().removeHandler(self.stdout_log_handler)
        logging.getLogger().removeHandler(self.error_log_handler)
        if self.expect_no_errors:
            self.assert_no_errors()

    def assert_no_errors(self):
        length = self.error_buffer.tell()
        assert length == 0, 'There were errors in the log'
        self.expect_no_errors = False

    def assert_errors(self):
        length = self.error_buffer.tell()
        assert length > 0, 'No errors in logs'
        self.expect_no_errors = False
