import json
import logging
import unittest
import sys

from .test_formatter import MockLoggingHandler
from flywheel_common.logging.extra_formatter import wrap_default_handler
from flywheel_common.logging.context_logger import LoggerContextAdapter

LoggerClass = logging.getLoggerClass()

class ExtrasWrapperTestCases(unittest.TestCase):
    def setUp(self):
        # Define logger
        self.log = LoggerClass(__name__)
        self.handler = MockLoggingHandler()
        self.log.addHandler(self.handler)
        self.log.setLevel('DEBUG')

        wrap_default_handler(self.log)

    def test_message(self):
        self.assertIsNotNone(self.handler.formatter)

        # No extras
        self.log.debug('msg=%s log message', 'Debug')
        string_log_record = self.handler.messages['debug'][0]
        self.assertEqual(string_log_record, 'msg=Debug log message')

        # Extra context
        self.log.debug('This message has context', extra={'context': {'foo': 5}})
        string_log_record = self.handler.messages['debug'][1]
        self.assertEqual(string_log_record, 'This message has context; foo=5')

    def test_context_logger(self):
        log = LoggerContextAdapter(self.log, context={'test': 'message'})

        # Extra context
        log.debug('Context test')
        string_log_record = self.handler.messages['debug'][0]
        self.assertEqual(string_log_record, 'Context test; test=message')
