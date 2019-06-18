# Copyright 2018      Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.
from io import StringIO
import logging
import unittest
from unittest import mock

import upt


class TestLog(unittest.TestCase):
    @mock.patch('sys.stderr', new_callable=StringIO)
    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_quiet(self, m_stdout, m_stderr):
        logger = upt.log.create_logger(logging.CRITICAL+1)
        logger.debug('debug')
        logger.info('info')
        logger.warning('warning')
        logger.error('error')
        logger.critical('critical')
        self.assertEqual(m_stdout.getvalue(), '')
        self.assertEqual(m_stderr.getvalue(), '')

    @mock.patch('sys.stderr', new_callable=StringIO)
    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_debug(self, m_stdout, m_stderr):
        logger = upt.log.create_logger(logging.DEBUG)
        logger.debug('debug')
        logger.info('info')
        logger.warning('warning')
        logger.error('error')
        logger.critical('critical')
        self.assertEqual(m_stdout.getvalue(), 'debug\ninfo\nwarning\n')
        self.assertEqual(m_stderr.getvalue(), 'error\ncritical\n')

    @mock.patch('sys.stderr', new_callable=StringIO)
    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_set_formatter(self, m_stdout, m_stderr):
        logger = upt.log.create_logger(logging.DEBUG)
        upt.log.logger_set_formatter(logger, 'foo')
        logger.debug('debug')
        logger.error('error')
        self.assertEqual(m_stdout.getvalue(), '[DEBUG   ] [foo] debug\n')
        self.assertEqual(m_stderr.getvalue(), '[ERROR   ] [foo] error\n')


if __name__ == '__main__':
    unittest.main()
