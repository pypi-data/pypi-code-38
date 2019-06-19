##############################################################################
#
# Copyright (c) 2019 Vifib SARL and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from slapos.grid.promise import PromiseError
from slapos.test.promise.plugin import TestPromisePluginMixin

import tempfile
import os
import unittest
import shutil


class TestCheckFileState(TestPromisePluginMixin):
  def setUp(self):
    TestPromisePluginMixin.setUp(self)
    self.tempdir = tempfile.mkdtemp()
    self.promise_name = "check-file-state.py"

    self.base_content = """from slapos.promise.plugin.check_file_state import RunPromise

extra_config_dict = {
  'filename': %(filename)r,
  'state': %(state)r,
  'url': %(url)r,
}
"""

  def tearDown(self):
    TestPromisePluginMixin.tearDown(self)
    shutil.rmtree(self.tempdir)

  def test_check_file_directory(self):
    filename = os.path.join(self.tempdir, 'test.file')
    os.mkdir(filename)
    content = self.base_content % {
      'filename': filename,
      'state': 'not-empty',
      'url': 'https://www.example.com/',
    }
    self.writePromise(self.promise_name, content)
    self.configureLauncher()
    with self.assertRaises(PromiseError):
      self.launcher.run()
    result = self.getPromiseResult(self.promise_name)
    self.assertEqual(result['result']['failed'], True)
    self.assertEqual(
      result['result']['message'],
      "ERROR IOError(21, 'Is a directory') "
      "during opening and reading file %r" % (filename,)
    )

  def test_check_file_not_exists(self):
    filename = os.path.join(self.tempdir, 'test.file')
    content = self.base_content % {
      'filename': filename,
      'state': 'not-empty',
      'url': 'https://www.example.com/',
    }
    self.writePromise(self.promise_name, content)
    self.configureLauncher()
    with self.assertRaises(PromiseError):
      self.launcher.run()
    result = self.getPromiseResult(self.promise_name)
    self.assertEqual(result['result']['failed'], True)
    self.assertEqual(
      result['result']['message'],
      "ERROR IOError(2, 'No such file or directory') "
      "during opening and reading file %r" % (filename,)
    )

  def test_check_file_empty(self):
    filename = os.path.join(self.tempdir, 'test.file')
    with open(filename, 'w') as fh:
      fh.write('')
    content = self.base_content % {
      'filename': filename,
      'state': 'empty',
      'url': 'https://www.example.com/',
    }
    self.writePromise(self.promise_name, content)
    self.configureLauncher()
    self.launcher.run()
    result = self.getPromiseResult(self.promise_name)
    self.assertEqual(result['result']['failed'], False)
    self.assertEqual(
      result['result']['message'],
      "OK %r state 'empty'" % (filename,)
    )

  def test_check_file_not_empty_fail(self):
    filename = os.path.join(self.tempdir, 'test.file')
    with open(filename, 'w') as fh:
      fh.write('')
    content = self.base_content % {
      'filename': filename,
      'state': 'not-empty',
      'url': 'https://www.example.com/',
    }
    self.writePromise(self.promise_name, content)
    self.configureLauncher()
    with self.assertRaises(PromiseError):
      self.launcher.run()
    result = self.getPromiseResult(self.promise_name)
    self.assertEqual(result['result']['failed'], True)
    self.assertEqual(
      result['result']['message'],
      "ERROR %r empty" % (filename,)
    )

  def test_check_file_not_empty(self):
    filename = os.path.join(self.tempdir, 'test.file')
    with open(filename, 'w') as fh:
      fh.write('content')
    content = self.base_content % {
      'filename': filename,
      'state': 'not-empty',
      'url': 'https://www.example.com/',
    }
    self.writePromise(self.promise_name, content)
    self.configureLauncher()
    self.launcher.run()
    result = self.getPromiseResult(self.promise_name)
    self.assertEqual(result['result']['failed'], False)
    self.assertEqual(
      result['result']['message'],
      "OK %r state 'not-empty'" % (filename,)
    )

  def test_check_file_empty_fail(self):
    filename = os.path.join(self.tempdir, 'test.file')
    with open(filename, 'w') as fh:
      fh.write('content')
    content = self.base_content % {
      'filename': filename,
      'state': 'empty',
      'url': 'https://www.example.com/',
    }
    self.writePromise(self.promise_name, content)
    self.configureLauncher()
    with self.assertRaises(PromiseError):
      self.launcher.run()
    result = self.getPromiseResult(self.promise_name)
    self.assertEqual(result['result']['failed'], True)
    self.assertEqual(
      result['result']['message'],
      "ERROR %r not empty, content available at "
      "https://www.example.com/" % (filename,)
    )


if __name__ == '__main__':
  unittest.main()
