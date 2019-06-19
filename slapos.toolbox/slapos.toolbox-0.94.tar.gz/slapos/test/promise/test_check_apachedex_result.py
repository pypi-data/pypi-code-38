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
from slapos.promise.check_apachedex_result import checkApachedexResult

apdex_not_found_message = "No result found in the apdex file or the file is corrupted"
low_score_message_formater = "Score too low: {}% - Threshold: {}%"
ok_message_formater = "OK - Score: {}%"
skip_message = "Instance has been just deployed. Skipping check.."

class TestCheckApacheDigestResult(unittest.TestCase):

  def _create_file(self, date, with_content):
    content = ''
    if with_content:
      with open(self.base_path + "/apachedex.html") as f:
        content = f.read()

    name = date.strftime('ApacheDex-%Y-%m-%d.html')
    oldtime = time.mktime(date.timetuple()) + 2000
    with open( self.base_dir+name, 'a') as the_file:
      the_file.write(content)
    os.utime(self.base_dir+name, ( oldtime , oldtime ))
    
  def _remove_file(self, date):
    name = date.strftime('ApacheDex-%Y-%m-%d.html')
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
    status, message = checkApachedexResult(self.base_dir, self.status_file, 60)
    self.assertEqual(ok_message_formater.format(80), message)
    self.assertEqual(0, status)

  def test_no_today_file_and_empty_yesterday_file(self):
    self._remove_file(self.today)
    status, message = checkApachedexResult(self.base_dir, self.status_file, 60)
    self.assertEqual(apdex_not_found_message, message)
    self.assertEqual(1, status)
    self._create_file(self.today, True)

  def test_threshold_is_lower(self):
    threshold = 90.0
    status, message = checkApachedexResult(self.base_dir, self.status_file, threshold)
    self.assertEqual(low_score_message_formater.format(80, threshold), message)
    self.assertEqual(1, status)

  def test_no_today_file_but_yesterday_file(self):
    self._remove_file(self.today)
    self._create_file(self.yesterday, True)
    status, message = checkApachedexResult(self.base_dir, self.status_file, 60)
    self.assertEqual(ok_message_formater.format(80), message)
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

