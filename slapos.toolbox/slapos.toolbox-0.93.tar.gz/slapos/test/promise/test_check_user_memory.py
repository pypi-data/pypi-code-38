##############################################################################
#
# Copyright (c) 2018 Vifib SARL and Contributors. All Rights Reserved.
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
from datetime import datetime

from slapos.test.promise import data
from slapos.promise.check_user_memory import getMemoryInfo, checkMemoryUsage

no_result_message = "No result found in collector.db."

class TestUserMemory(unittest.TestCase):

  def setUp(self):
    self.base_path = "/".join(data.__file__.split("/")[:-1])
    self.status = "ok"
    self.db_file = '/tmp/collector.db'
    self.db_dir = os.path.dirname(self.db_file)

    # populate db
    self.conn = sqlite3.connect(self.db_file)
    f = open(self.base_path+"/memtest.sql")
    sql = f.read()
    self.conn.executescript(sql)
    self.conn.close()

  def test_check_memory(self):
    self.assertEqual(
      ({
        'byte': 29544162598,
        'percent': 87.65432099725093,
      }, ""),
      getMemoryInfo(
        self.db_dir,
        datetime(2017, 9, 15, 0, 2, 0),
        'slaptestuser1',
      ),
    )
    self.assertEqual(
      (True, "User memory usage: 29544162598B (87.7%)", ""),
      checkMemoryUsage(
        self.db_dir,
        datetime(2017, 9, 15, 0, 2, 0),
        'slaptestuser1',
        threshold=29600000000,
      ),
    )
    self.assertEqual(
      (True, "User memory usage: 87.7% (29544162598B)", ""),
      checkMemoryUsage(
        self.db_dir,
        datetime(2017, 9, 15, 0, 2, 0),
        'slaptestuser1',
        threshold=88,
        unit="percent",
      ),
    )
    self.assertEqual(
      (False, "High user memory usage: 29544162598B (87.7%)", ""),
      checkMemoryUsage(
        self.db_dir,
        datetime(2017, 9, 15, 0, 2, 0),
        'slaptestuser1',
        threshold=29500000000,
      ),
    )
    self.assertEqual(
      (False, "High user memory usage: 87.7% (29544162598B)", ""),
      checkMemoryUsage(
        self.db_dir,
        datetime(2017, 9, 15, 0, 2, 0),
        'slaptestuser1',
        threshold=87,
        unit="percent",
      ),
    )

  def test_check_memory_with_unavailable_dates(self):
    self.assertEqual(
      (False, "error", no_result_message),
      checkMemoryUsage(self.db_dir, datetime(2017, 9, 14, 18, 0 , 0), "slaptestuser1", 1.0),
    )

  def tearDown(self):
    if os.path.exists(self.db_file):
      os.remove(self.db_file)
if __name__ == '__main__':
  unittest.main()

