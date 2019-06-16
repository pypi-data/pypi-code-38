# -*- coding: utf-8; -*-

from __future__ import unicode_literals, absolute_import

import logging
from unittest import TestCase
from six import StringIO

import six
from mock import patch

from rattail import logging as rattail_logging


class TestLogging(TestCase):

    @patch('rattail.logging.os')
    @patch('rattail.logging.sys')
    @patch('rattail.logging.socket')
    @patch('rattail.logging.getpass')
    def test_adapter_adds_all_context(self, getpass, socket, sys, os):
        socket.getfqdn.return_value = 'testing.rattailproject.org'
        socket.gethostbyname.return_value = '127.0.0.1'
        sys.argv = ['just', 'testing']
        os.getuid.return_value = 420
        getpass.getuser.return_value = 'joeschmoe'
        formatter = logging.Formatter(u"%(hostname)s %(hostip)s %(argv)s %(username)s %(uid)s %(levelname)s %(message)s")
        string = StringIO()
        handler = logging.StreamHandler(string)
        handler.setFormatter(formatter)
        log = logging.getLogger('fake_for_testing')
        log.addHandler(handler)
        log.propagate = False
        log = rattail_logging.RattailAdapter(log)
        self.assertEqual(string.getvalue(), "")
        log.debug("some random thing")
        if six.PY3:
            self.assertEqual(string.getvalue(), "testing.rattailproject.org 127.0.0.1 ['just', 'testing'] joeschmoe 420 DEBUG some random thing\n")
        else:
            self.assertEqual(string.getvalue(), "testing.rattailproject.org 127.0.0.1 [u'just', u'testing'] joeschmoe 420 DEBUG some random thing\n")
        handler.close()
        string.close()
