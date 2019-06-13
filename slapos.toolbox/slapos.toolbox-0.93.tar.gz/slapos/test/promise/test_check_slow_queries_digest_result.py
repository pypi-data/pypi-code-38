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
import os
import time
import tempfile
import datetime
import shutil

from slapos.test.promise import data
from slapos.promise.check_slow_queries_digest_result import checkMariadbDigestResult

class TestCheckSlowQueriesDigestResult(unittest.TestCase):

  def _create_file(self, date, with_content):
    content = ''
    if with_content:
      with open(self.base_path + "/ptdigest.html") as f:
        content = f.read()

    name = date.strftime('slowquery_digest.txt-%Y-%m-%d')
    oldtime = time.mktime(date.timetuple()) + 2000
    with open( self.base_dir+name, 'a') as the_file:
      the_file.write(content)
    os.utime(self.base_dir+name, ( oldtime , oldtime ))
    
  def _remove_file(self, date):
    name = date.strftime('slowquery_digest.txt-%Y-%m-%d')
    os.remove(self.base_dir+name)

  def setUp(self):

    self.base_path = "/".join(data.__file__.split("/")[:-1])
    self.base_dir = "/tmp/ap/"
    if not os.path.exists(self.base_dir):
      os.makedirs(self.base_dir)
      os.utime(self.base_dir, (time.time() - 202800, time.time() - 202800))

    # create test files
    self.today = datetime.date.today()
    self._create_file(self.today, True)

    self.yesterday = (self.today - datetime.timedelta(1))
    self._create_file(self.yesterday, False)
    _, self.status_file = tempfile.mkstemp()

  def test_threshold_is_greater(self):
    status, message = checkMariadbDigestResult(self.base_dir, self.status_file, 5000, 100)
    self.assertEqual("Thanks for keeping it all clean, total queries are : 3420.0 slowest query time is : 34", message)
    self.assertEqual(0, status)

  def test_no_today_file_and_empty_yesterday_file(self):
    self._remove_file(self.today)
    status, message = checkMariadbDigestResult(self.base_dir, self.status_file, 60, 100)
    self.assertEqual("No result found in the slow query digest file or the file is corrupted", message)
    self.assertEqual(1, status)
    self._create_file(self.today, True)

  def test_fail(self):
    status, message = checkMariadbDigestResult(self.base_dir, self.status_file, 90, 100)
    self.assertEqual("Threshold is lower than expected: \nExpected total queries : 90 and current is: 3420.0\nExpected slowest query : 100 and current is: 34", message)
    self.assertEqual(1, status)

  def test_no_today_file_but_yesterday_file(self):
    self._remove_file(self.today)
    self._create_file(self.yesterday, True)
    status, message = checkMariadbDigestResult(self.base_dir, self.status_file, 5000, 100)
    self.assertEqual("Thanks for keeping it all clean, total queries are : 3420.0 slowest query time is : 34", message)
    self.assertEqual(0, status)
    self._create_file(self.today, True)
    self._remove_file(self.yesterday)
    self._create_file(self.yesterday, False)
    
  def tearDown(self):
    self._remove_file(self.today)
    self._remove_file(self.yesterday)
    shutil.rmtree('/tmp/ap')

if __name__ == '__main__':
  unittest.main()

