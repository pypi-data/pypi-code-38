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
import socket
import time
import psutil
from slapos.promise.apache_mpm_watchdog import watchServerStatus, \
  loadJSONFile, writeJSONFile, getServerStatus, search_pid_regex

from slapos.test.promise import data

class TestApacheMPMWatchdog(unittest.TestCase):

  def setUp(self):
    self.base_path = "/".join(data.__file__.split("/")[:-1])

  def text_searchPidRegex(self):

    with open(self.base_path + "/server_status.html") as f:
      server_status = f.read()
      f.close()

    self.assertEqual(['12345', '12346'], 
      re.findall(search_pid_regex, server_status))

    

  def test_loadJSONFile(self):
    self.assertEqual({},
       loadJSONFile("couscous"))

    self.assertEqual(
      {"1234": 1496161635.514768 , "4321": 1496161635.514768},
      loadJSONFile(os.path.join(self.base_path, "test_db.json")))

    self.assertEqual(
      {},
      loadJSONFile(os.path.join(self.base_path, "corrupted_db.json")))

  def test_writeJSONFile(self):
    # Check if don't raise.
    self.assertEqual(None,
      writeJSONFile({}, None))

    current_pid = os.getpid() 
    self.assertEqual(None,
      writeJSONFile({"123482": 123, current_pid: 124},
          os.path.join(self.base_path, "write_db.json")))

    with open(os.path.join(self.base_path, "write_db.json")) as f:
      json_content = f.read()
      f.close()

    self.assertEqual(json_content,
      '{"%s": 124}' % current_pid)


  def test_getServerStatus(self):
    self.assertEqual(None,
        getServerStatus("http://localhost/", None, None))
    self.assertEqual(None,
        getServerStatus("http://localhost/", 
                           "user", "password"))
    self.assertNotEquals(None,
        getServerStatus("https://www.erp5.com/", None, None))


if __name__ == '__main__':
  unittest.main()

