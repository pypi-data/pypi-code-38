# -*- coding: utf-8; -*-

from __future__ import unicode_literals, absolute_import

from six.moves import queue
from unittest import TestCase

from mock import Mock
from fixture import TempIO

from rattail.config import make_config
from rattail.filemon import linux
from rattail.filemon.config import Profile


class TestEventHandler(TestCase):

    def setUp(self):
        self.tmp = TempIO()
        self.config = make_config([])
        self.config.set(u'rattail.filemon', u'monitor', u'foo')
        self.config.set(u'rattail.filemon', u'foo.dirs', self.tmp)
        self.config.set(u'rattail.filemon', u'foo.actions', u'noop')
        self.config.set(u'rattail.filemon', u'foo.action.noop.func', u'rattail.filemon.actions:noop')
        self.profile = Profile(self.config, u'foo')
        self.profile.queue = queue.Queue()
        self.handler = linux.EventHandler()
        self.handler.my_init(self.profile)

    def test_in_access_event_does_nothing(self):
        event = Mock(pathname=self.tmp.putfile(u'file', u''))
        self.handler.process_IN_ACCESS(event)
        self.assertTrue(self.profile.queue.empty())

    def test_in_attrib_event_does_nothing(self):
        event = Mock(pathname=self.tmp.putfile(u'file', u''))
        self.handler.process_IN_ATTRIB(event)
        self.assertTrue(self.profile.queue.empty())

    def test_in_create_event_does_nothing(self):
        event = Mock(pathname=self.tmp.putfile(u'file', u''))
        self.handler.process_IN_CREATE(event)
        self.assertTrue(self.profile.queue.empty())

    def test_in_modify_event_does_nothing(self):
        event = Mock(pathname=self.tmp.putfile(u'file', u''))
        self.handler.process_IN_MODIFY(event)
        self.assertTrue(self.profile.queue.empty())

    def test_in_close_write_event_queues_file_if_profile_does_not_watch_locks(self):
        event = Mock(pathname=self.tmp.putfile(u'file', u''))
        self.profile.watch_locks = False
        self.handler.process_IN_CLOSE_WRITE(event)
        self.assertEqual(self.profile.queue.qsize(), 1)
        self.assertEqual(self.profile.queue.get_nowait(), self.tmp.join(u'file'))

    def test_in_close_write_event_does_nothing_if_profile_watches_locks(self):
        event = Mock(pathname=self.tmp.putfile(u'file.lock', u''))
        self.profile.watch_locks = True
        self.handler.process_IN_CLOSE_WRITE(event)
        self.assertTrue(self.profile.queue.empty())

    def test_in_moved_to_event_queues_file_if_profile_does_not_watch_locks(self):
        event = Mock(pathname=self.tmp.putfile(u'file', u''))
        self.profile.watch_locks = False
        self.handler.process_IN_MOVED_TO(event)
        self.assertEqual(self.profile.queue.qsize(), 1)
        self.assertEqual(self.profile.queue.get_nowait(), self.tmp.join(u'file'))

    def test_in_moved_to_event_does_nothing_if_profile_watches_locks(self):
        event = Mock(pathname=self.tmp.putfile(u'file.lock', u''))
        self.profile.watch_locks = True
        self.handler.process_IN_MOVED_TO(event)
        self.assertTrue(self.profile.queue.empty())

    def test_in_delete_event_queues_file_if_profile_watches_locks(self):
        event = Mock(pathname=self.tmp.putfile(u'file.lock', u''))
        self.profile.watch_locks = True
        self.handler.process_IN_DELETE(event)
        self.assertEqual(self.profile.queue.qsize(), 1)
        self.assertEqual(self.profile.queue.get_nowait(), self.tmp.join(u'file'))

    def test_in_moved_to_event_does_nothing_if_profile_does_not_watch_locks(self):
        event = Mock(pathname=self.tmp.putfile(u'file', u''))
        self.profile.watch_locks = False
        self.handler.process_IN_DELETE(event)
        self.assertTrue(self.profile.queue.empty())
