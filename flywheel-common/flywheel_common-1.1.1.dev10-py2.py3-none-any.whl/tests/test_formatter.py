import json
import logging
import unittest
import sys

LoggerClass = logging.getLoggerClass()

from flywheel_common.logging.json_formatter import JSONLogFormatter
from flywheel_common.logging.context_logger import LoggerContextAdapter

class MockLoggingHandler(logging.Handler):
    """Mock logging handler to check for expected logs."""

    def __init__(self, *args, **kwargs):
        self.messages = {
            'debug': [],
            'info': [],
            'warning': [],
            'error': [],
            'critical': [],
        }
        logging.Handler.__init__(self, *args, **kwargs)

    def emit(self, record):
        self.messages[record.levelname.lower()].append(self.formatter.format(record))

class FormatterTestCases(unittest.TestCase):
    def setUp(self):
        # Define logger
        log = LoggerClass(__name__)
        self.handler = MockLoggingHandler()
        self.formatter = JSONLogFormatter()
        self.handler.setFormatter(self.formatter)
        log.addHandler(self.handler)
        log.setLevel('DEBUG')

        self.log = LoggerContextAdapter(log)

    def set_context(self, **kwargs):
        self.log = self.log.with_context(**kwargs)

    def test_message(self):
        self.set_context(job=1)
        self.log.debug('%s log message', 'Debug')
        string_log_record = self.handler.messages['debug'][0]
        log_record = json.loads(string_log_record)
        self.assertEqual(log_record['message'], 'Debug log message')
        self.assertEqual(log_record['severity'], 'DEBUG')
        self.assertEqual(log_record['job'], 1)

    def test_record_attributes(self):
        self.set_context(origin='user:user@user.com')
        self.log.error(str(Exception('Oh no')))

        string_log_record = self.handler.messages['error'][0]
        log_record = json.loads(string_log_record)

        self.assertEqual(log_record['origin'], 'user:user@user.com')
        self.assertEqual(log_record['filename'], 'test_formatter.py')
        self.assertEqual(log_record['lineno'], 53)

    def test_non_context_logs(self):
        a= {}
        try:
            b = a['p']
        except KeyError as e:
            self.log.warning(e, exc_info=True)

        string_log_record = self.handler.messages['warning'][0]
        log_record = json.loads(string_log_record)

        self.assertTrue(log_record['message'])
        self.assertTrue(log_record.get('exc_info'))

    def test_unspecified_reocrd_fields(self):
        self.set_context(custom_field='custom_value')
        self.log.debug('Hello')

        log_record = json.loads(self.handler.messages['debug'][0])

        self.assertEqual(log_record['message'], 'Hello')
        self.assertEqual(log_record['custom_field'], 'custom_value')

    def test_tagged_logging(self):
        formatter = JSONLogFormatter(tag='flywheel')
        self.handler.setFormatter(formatter)
        self.log.debug('Hello')

        string_log_record = self.handler.messages['debug'][0]
        record_parts = string_log_record.split(':')
        tag = record_parts[0]
        json_record = json.loads(':'.join(record_parts[1:]))
        self.assertEqual(tag, 'flywheel')
        self.assertEqual(json_record['message'], 'Hello')

        self.handler.setFormatter(self.formatter)
