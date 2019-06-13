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
import sqlite3

from slapos.test.promise import data
from slapos.promise.check_computer_memory import getMemoryInfo, checkMemoryUsage

total_memory_fetch_failure_message = "couldn't fetch total memory, collectordb is empty?"

class TestComputerMemory(unittest.TestCase):

  def setUp(self):
    self.base_path = "/".join(data.__file__.split("/")[:-1])
    self.status = "ok"
    self.db_file = '/tmp/collector.db'

    # populate db
    self.conn = sqlite3.connect(self.db_file)
    f = open(self.base_path+"/memtest.sql")
    sql = f.read()
    self.conn.executescript(sql)
    self.conn.close() 

  def test_check_memory(self):
    self.assertEqual(
      ({
        'total': 33705312256,
        'used': 33139023872,
        'used_percent': 98.31988388151132,
        'free': 566288384,
        'free_percent': 1.6801161184886904,
      }, ""),
      getMemoryInfo('/tmp', '00:02', '2017-09-15'))
    self.assertEqual(
      (True, "OK - memory used: 33139023872B of 33705312256B (98.3%)", ""),
      checkMemoryUsage('/tmp', '00:02', '2017-09-15', threshold=33500000000),
    )
    self.assertEqual(
      (True, "OK - memory used: 98.3% (33139023872B of 33705312256B)", ""),
      checkMemoryUsage('/tmp', '00:02', '2017-09-15', threshold=99, unit="percent"),
    )
    self.assertEqual(
      (True, "OK - free memory: 566288384B of 33705312256B (1.7%)", ""),
      checkMemoryUsage('/tmp', '00:02', '2017-09-15', threshold=500000000, key="free"),
    )
    self.assertEqual(
      (True, "OK - free memory: 1.7% (566288384B of 33705312256B)", ""),
      checkMemoryUsage('/tmp', '00:02', '2017-09-15', threshold=1, key="free", unit="percent"),
    )
    self.assertEqual(
      (False, "Low available memory - usage: 33139023872B of 33705312256B (98.3%)", ""),
      checkMemoryUsage('/tmp', '00:02', '2017-09-15', threshold=33000000000),
    )
    self.assertEqual(
      (False, "Low available memory - usage: 98.3% (33139023872B of 33705312256B)", ""),
      checkMemoryUsage('/tmp', '00:02', '2017-09-15', threshold=98, unit="percent"),
    )
    self.assertEqual(
      (False, "Low available memory - free: 566288384B of 33705312256B (1.7%)", ""),
      checkMemoryUsage('/tmp', '00:02', '2017-09-15', threshold=600000000, key="free"),
    )
    self.assertEqual(
      (False, "Low available memory - free: 1.7% (566288384B of 33705312256B)", ""),
      checkMemoryUsage('/tmp', '00:02', '2017-09-15', threshold=2, key="free", unit="percent"),
    )

  def test_check_memory_with_unavailable_dates(self):
    self.assertEqual(
      (False, "error", total_memory_fetch_failure_message),
      checkMemoryUsage('/tmp', '18:00', '2017-09-14', 1.0),
    )

  def tearDown(self):
    if os.path.exists(self.db_file):
      os.remove(self.db_file)
if __name__ == '__main__':
  unittest.main()

