# -*- coding: utf-8; -*-

from __future__ import unicode_literals, absolute_import

from six.moves import queue
from unittest import TestCase

from fixture import TempIO

from rattail.config import make_config
from rattail.filemon import util
from rattail.filemon.config import Profile


class TestQueueExisting(TestCase):

    def setUp(self):
        self.tmp = TempIO()
        self.config = make_config([])
        self.config.set(u'rattail.filemon', u'monitor', u'foo')
        self.config.set(u'rattail.filemon', u'foo.dirs', self.tmp)
        self.config.set(u'rattail.filemon', u'foo.actions', u'noop')
        self.config.set(u'rattail.filemon', u'foo.action.noop.func', u'rattail.filemon.actions:noop')
        self.profile = Profile(self.config, u'foo')
        self.profile.queue = queue.Queue()

    def test_nothing_queued_if_no_files_exist(self):
        util.queue_existing(self.profile, self.tmp)
        self.assertTrue(self.profile.queue.empty())

    def test_normal_files_are_queued_but_not_folders(self):
        self.tmp.putfile(u'file', u'')
        self.tmp.mkdir(u'folder')
        util.queue_existing(self.profile, self.tmp)
        self.assertEqual(self.profile.queue.qsize(), 1)
        self.assertEqual(self.profile.queue.get_nowait(), self.tmp.join(u'file'))
        self.assertTrue(self.profile.queue.empty())

    def test_if_profile_watches_locks_then_normal_files_are_queued_but_not_lock_files(self):
        self.profile.watch_locks = True
        self.tmp.putfile(u'file1.lock', u'')
        self.tmp.putfile(u'file2', u'')
        util.queue_existing(self.profile, self.tmp)
        self.assertEqual(self.profile.queue.qsize(), 1)
        self.assertEqual(self.profile.queue.get_nowait(), self.tmp.join(u'file2'))
        self.assertTrue(self.profile.queue.empty())
