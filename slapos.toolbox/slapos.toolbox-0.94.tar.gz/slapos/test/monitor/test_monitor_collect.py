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
import time

from slapos.test.promise import data
from slapos.monitor.collect import ResourceCollect

class TestMonitorCollect(unittest.TestCase):

  def setUp(self):
    self.base_path = "/".join(data.__file__.split("/")[:-1])
    self.status = "ok"

    # populate db
    self.conn = sqlite3.connect('/tmp/collector.db')
    f = open(self.base_path+"/monitor_collect.sql")
    sql = f.read()
    self.conn.executescript(sql)
    self.conn.close() 

    # inititalise
    self.collector = ResourceCollect('/tmp/')
    

  def test_getPartitionUsedMemoryAverage(self):
    self.assertEqual(1195.492578125,
      self.collector.getPartitionUsedMemoryAverage('slapuser15', '2017-09-16'))

  def test_getPartitionCPULoadAverage(self):
    self.assertEqual(2.1599999999999993,
      self.collector.getPartitionCPULoadAverage('slapuser15', '2017-09-16'))

  def test_getPartitionDiskUsedAverage(self):
    self.assertEqual(35.5234375,
      self.collector.getPartitionDiskUsedAverage('slapuser15', '2017-04-18'))

  def test_getPartitionConsumption(self):
    data = self.collector.getPartitionConsumption('slapuser15', date_scope='2017-09-16', 
                                             min_time='00:01:00', max_time='00:13:00')
    self.assertEqual(1302.66, data[0]['cpu_time'])
    self.assertEqual(26825304064.0, data[0]['io_rw_counter'])

  def test_getPartitionComsumptionStatus(self):
    data = self.collector.getPartitionComsumptionStatus('slapuser15', date_scope='2017-09-16',
                                         min_time='00:01:00', max_time='00:13:00')
    self.assertEqual(7.3, data[0]['cpu_percent'])
    self.assertEqual(2822535483392.0, data[2]['io_rw_counter'])

  def tearDown(self):
    os.remove("/tmp/collector.db") 
if __name__ == '__main__':
  unittest.main()

