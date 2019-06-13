# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2017 Vifib SARL and Contributors. All Rights Reserved.
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

import unittest
import os.path
import tempfile
import shutil
from datetime import date

from slapos.securedelete import getAgumentParser, shred

class TestSecureDelete(unittest.TestCase):
  def setUp(self):
    _, self.remove_file = tempfile.mkstemp()
    _, self.remove_file2 = tempfile.mkstemp()
    self.link_name = os.path.join(os.path.dirname(self.remove_file),
                                  '%s_link' % os.path.basename(self.remove_file))
    with open(self.remove_file, 'w') as f:
      f.write("Skjsds@ßdjierhjzlalaa...")
    with open(self.remove_file2, 'w') as f:
      f.write("Skjsds@ßdjiesdsdrhjzlalaa...")

  def tearDown(self):
    if os.path.exists(self.remove_file):
      os.remove(self.remove_file)
    if os.path.exists(self.remove_file2):
      os.remove(self.remove_file2)
    if os.path.exists(self.link_name):
      os.unlink(self.link_name)

  def test_secure_remove_file(self):
    options = getAgumentParser().parse_args(['-n', '2', '-u', '-z', '--file', self.remove_file])
    passes = 2 + 1 # Option -z is used, plus one more pass
    result = shred(options)
    self.assertFalse(os.path.exists(self.remove_file))
    self.assertTrue("pass %s/%s" % (passes, passes) in result)
    self.assertTrue("%s: removed" % os.path.basename(self.remove_file) in result)

  def test_secure_remove_file_keep_file(self):
    options = getAgumentParser().parse_args(['-n', '2', '-z', '--file', self.remove_file])
    passes = 2 + 1 # Option -z is used, plus one more pass
    result = shred(options)
    self.assertTrue(os.path.exists(self.remove_file))
    self.assertTrue("pass %s/%s" % (passes, passes) in result)
    self.assertFalse("%s: removed" % os.path.basename(self.remove_file) in result)

  def test_secure_remove_file_non_zero(self):
    options = getAgumentParser().parse_args(['-n', '2', '-u', '--file', self.remove_file])
    passes = 2
    result = shred(options)
    self.assertFalse(os.path.exists(self.remove_file))
    self.assertTrue("pass %s/%s" % (passes, passes) in result)
    self.assertTrue("%s: removed" % os.path.basename(self.remove_file) in result)

  def test_secure_remove_file_check_exist(self):
    options = getAgumentParser().parse_args(['-n', '2', '-u', '-s', '--file', 'random.txt', self.remove_file])
    passes = 2
    result = shred(options)
    self.assertFalse(os.path.exists(self.remove_file))
    self.assertTrue("pass %s/%s" % (passes, passes) in result)
    self.assertTrue("%s: removed" % os.path.basename(self.remove_file) in result)

  def test_secure_remove_file_check_exist_false(self):
    options = getAgumentParser().parse_args(['-n', '2', '-u', '--file', 'random.txt'])
    passes = 2
    with self.assertRaises(RuntimeError):
      result = shred(options)

  def test_secure_remove_file_with_link(self):
    options = getAgumentParser().parse_args(['-n', '2', '-u', '--file', self.link_name])
    passes = 2
    os.symlink(self.remove_file, self.link_name)
    result = shred(options)
    # shred removed link and target file
    self.assertFalse(os.path.exists(self.remove_file))
    self.assertFalse(os.path.exists(self.link_name))
    self.assertTrue("pass %s/%s" % (passes, passes) in result)
    self.assertTrue("%s: removed" % os.path.basename(self.remove_file) in result)

  def test_secure_remove_file_multiple_files(self):
    options = getAgumentParser().parse_args(['-n', '2', '-u', '-z', '--file', self.remove_file, self.remove_file2])
    passes = 2 + 1 # Option -z is used, plus one more pass
    result = shred(options)
    self.assertFalse(os.path.exists(self.remove_file))
    self.assertTrue("pass %s/%s" % (passes, passes) in result)
    self.assertTrue("%s: removed" % os.path.basename(self.remove_file) in result)

    self.assertFalse(os.path.exists(self.remove_file2))
    self.assertTrue("%s: removed" % os.path.basename(self.remove_file2) in result)

if __name__ == '__main__':
  unittest.main()
