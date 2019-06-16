# -*- coding: utf-8; -*-

from __future__ import unicode_literals, absolute_import

import os
from unittest import TestCase

import lockfile
from fixture import TempIO

from rattail import files


class TestLockingCopy(TestCase):

    def setUp(self):
        self.tmp = TempIO()
        self.src = self.tmp.mkdir(u'src')
        self.dst = self.tmp.mkdir(u'dst')
        self.src_file = self.src.putfile('somefile', '')

    def test_normal_copy_succeeds(self):
        files.locking_copy(self.src_file, self.dst)
        dst_file = os.path.join(self.dst, u'somefile')
        self.assertTrue(os.path.exists(dst_file))
        self.assertTrue(os.path.isfile(dst_file))
        self.assertFalse(os.path.exists(os.path.join(self.dst, u'somefile.lock')))
