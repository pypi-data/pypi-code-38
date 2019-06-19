##############################################################################
#
# Copyright (c) 2015 Vifib SARL and Contributors. All Rights Reserved.
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
from slapos.agent.agent import AutoSTemp, TestMap

TESTMAP_DICT = {
  "test-wendelin-software-release": {
    "url": "https://lab.nexedi.com/nexedi/slapos/raw/1.0/software/wendelin/software.cfg", 
    "supply_computer": "COMP-2", 
    "group": "COMP-2", 
    "title": "test-wendelin-software-release"}, 
  "test-agent-software-release": {
    "url": "https://lab.nexedi.com/nexedi/slapos/raw/1.0/software/agent/software.cfg", 
    "supply_computer": "COMP-2", 
    "group": "COMP-2", 
    "title": "test-agent-software-release"}, 
  "test-powerdns-software-release": {
    "url": "https://lab.nexedi.com/nexedi/slapos/raw/1.0/software/powerdns/software.cfg", 
    "supply_computer": "COMP-2", 
    "group": "COMP-2", 
    "title": "test-powerdns-software-release"}, 
  "test-monitor-software-release": {
    "url": "https://lab.nexedi.com/nexedi/slapos/raw/1.0/software/monitor/software.cfg", 
    "supply_computer": "COMP-2", 
    "group": "COMP-2", 
    "title": "test-monitor-software-release"}, 
  "test-slapos-master-software-release": {
    "url": "https://lab.nexedi.com/nexedi/slapos/raw/1.0/software/slapos-master/software.cfg", 
    "supply_computer": "COMP-1", 
    "group": "COMP-1", 
    "title": "test-slapos-master-software-release"}, 
  "test-webrunner-software-release": {
    "url": "https://lab.nexedi.com/nexedi/slapos/raw/1.0/software/slaprunner/software.cfg", 
    "supply_computer": "COMP-1", 
    "group": "COMP-1", 
    "title": "test-webrunner-software-release"}, 
  "test-re6stnetmaster-software-release": {
    "url": "https://lab.nexedi.com/nexedi/slapos/raw/1.0/software/re6stnet/software.cfg", 
    "supply_computer": "COMP-2", 
    "group": "COMP-2", 
    "title": "test-re6stnetmaster-software-release"}, 
  "test-erp5testnode-software-release": {
    "url": "https://lab.nexedi.com/nexedi/slapos/raw/1.0/software/erp5testnode/software.cfg", 
    "supply_computer": "COMP-1", 
    "group": "COMP-1", 
    "title": "test-erp5testnode-software-release"}, 
  "test-apache-frontend-software-release": {
    "url": "https://lab.nexedi.com/nexedi/slapos/raw/1.0/software/apache-frontend/software.cfg", 
    "supply_computer": "COMP-1", 
    "group": "COMP-1", 
    "title": "test-apache-frontend-software-release"}, 
  "test-nayuos-software-release": {
    "url": "https://lab.nexedi.com/nexedi/slapos/raw/1.0/software/nayuos/software.cfg", 
    "supply_computer": "COMP-1", 
    "group": "COMP-1", 
    "title": "test-nayuos-software-release"}
  }



class TestTestMap(unittest.TestCase):

  def setUp(self):
    self.test_map = TestMap(TESTMAP_DICT)

  def test_group(self):
    """ Check available group of tests """
    self.assertEqual(self.test_map.getGroupList(), 
          ["COMP-1", "COMP-2"])

  def test_getnextgroup(self):
    """ Get Next Group """
    self.assertEqual(self.test_map.getNextGroup([]),
      "COMP-1")
    self.assertEqual(
      self.test_map.getNextGroup(ignore_list=["COMP-1"]),
      "COMP-2")

  def test_getexcludelist(self):
    """ Check available group of tests """
    self.assertEqual(self.test_map.getExcludeList("COMP-1"),
      set(['test-agent-software-release',
           'test-wendelin-software-release',
           'test-monitor-software-release',
           'test-re6stnetmaster-software-release',
           'test-powerdns-software-release']))
    self.assertEqual(
      self.test_map.getExcludeList("COMP-2"),
      set(['test-apache-frontend-software-release',
           'test-slapos-master-software-release',
           'test-webrunner-software-release',
           'test-erp5testnode-software-release',
           'test-apache-frontend-software-release',
           'test-nayuos-software-release']))

    self.test_map.addRanTest('test-agent-software-release')
    self.assertEqual(
      self.test_map.getExcludeList("COMP-2"),
      set(['test-apache-frontend-software-release',
           'test-slapos-master-software-release',
           'test-webrunner-software-release',
           'test-erp5testnode-software-release',
           'test-apache-frontend-software-release',
           'test-nayuos-software-release',
           'test-agent-software-release']))

  def test_dropgroup(self):
    """ Check available group of tests """
    test_map_copy = TestMap(TESTMAP_DICT)
    self.assertEqual(test_map_copy.getGroupList(),
          ["COMP-1", "COMP-2"])

    test_map_copy.dropGroup("COMP-1")
    self.assertEqual(test_map_copy.getGroupList(),
          ["COMP-2"])

  def test_cleanup_empty_group(self):
    """ Check available group of tests """
    test_map_copy = TestMap(TESTMAP_DICT)
    test_map_copy.test_map_dict["NEWGROUP"] = {}
    self.assertEqual(test_map_copy.getGroupList(),
          ["COMP-1", "COMP-2", "NEWGROUP"])

    test_map_copy.cleanEmptyGroup()
    self.assertEqual(test_map_copy.getGroupList(),
          ["COMP-1", "COMP-2"])

class TestAutoSTemp(unittest.TestCase):

  def test_autostemp(self):
    """ Test AutoSTemp creates the file with content and
        removes it when deleted.
    """
    f = AutoSTemp("foo")
    self.assertEqual(open(f.name, "r").read(), "foo")
    fname = f.name
    self.assertTrue(os.path.isfile(fname))
    del f
    self.assertFalse(os.path.isfile(fname))

if __name__ == '__main__':
  unittest.main()
