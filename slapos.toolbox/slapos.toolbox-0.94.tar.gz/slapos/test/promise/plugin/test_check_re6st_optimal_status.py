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

from slapos.test.promise.plugin import TestPromisePluginMixin
from slapos.grid.promise import PromiseError
import os

class TestCheckRe6stOptimalStatus(TestPromisePluginMixin):

  def setUp(self):
    TestPromisePluginMixin.setUp(self)
    self.promise_name = "check-icmp-packet-lost.py"

    self.base_content = """from slapos.promise.plugin.check_re6st_optimal_status import RunPromise

extra_config_dict = {
  'ipv4': '%(ipv4)s',
  'count': '%(count)s',
  'ipv6': '%(ipv6)s',
}
"""

  def tearDown(self):
    TestPromisePluginMixin.tearDown(self)

  def test_ipv6_is_faster(self):
    content = self.base_content % {
      'ipv4': "8.8.8.8",
      'ipv6': '::1',
      'count': 5,
    }
    self.writePromise(self.promise_name, content)

    self.configureLauncher(force=True, timeout=20, enable_anomaly=True)
    self.launcher.run()
    # run a second time to add more results
    self.launcher.run()
    result = self.getPromiseResult(self.promise_name)
    last_message = result['result']['message'].split('\n')[-1]
    self.assertEqual(result['result']['failed'], False)
    #self.assertEqual(last_message, "OK: IPv4 reachable, IPv6 reachable")
    # some testnodes cannot ping because they are qemu VM with Nat network, and
    # ICMP is disabled. Expected result is "OK: IPv4 reachable, IPv6 reachable"
    # but it ICMP is not working, we will have "IPv4 unreachable" in the message
    # so we will test only if the ping returned "OK" and if IPv6 was reachable.
    self.assertTrue(last_message.startswith("OK:"))
    self.assertTrue("IPv6 reachable" in last_message)

  def test_ipv4_is_faster(self):
    content = self.base_content % {
      'ipv4': "127.0.0.1",
      'ipv6': '2001:67c:1254::1',
      'count': 5,
    }
    self.writePromise(self.promise_name, content)

    self.configureLauncher(force=True, timeout=20, enable_anomaly=True)
    self.launcher.run()
    with self.assertRaises(PromiseError):
      self.launcher.run()
    result = self.getPromiseResult(self.promise_name)
    last_message = result['result']['message'].split('\n')[-1]
    self.assertEqual(result['result']['failed'], True)
    self.assertTrue(last_message.startswith('FAIL'))

  def test_ipv4_unreacheable_and_ipv6_ok(self):
    content = self.base_content % {
      'ipv4': "couscous",
      'ipv6': '::1',
      'count': 5,
    }
    self.writePromise(self.promise_name, content)

    self.configureLauncher(force=True, timeout=20, enable_anomaly=True)
    self.launcher.run()
    # run a second time to add more results
    self.launcher.run()
    result = self.getPromiseResult(self.promise_name)
    last_message = result['result']['message'].split('\n')[-1]
    self.assertEqual(result['result']['failed'], False)
    self.assertEqual(last_message, "OK: IPv4 unreachable, IPv6 reachable")

  def test_ipv6_fail(self):
    content = self.base_content % {
      'ipv4': "127.0.0.1",
      'ipv6': 'couscous',
      'count': 5,
    }
    self.writePromise(self.promise_name, content)

    self.configureLauncher(force=True, timeout=20, enable_anomaly=True)
    self.launcher.run()
    with self.assertRaises(PromiseError):
      self.launcher.run()
    result = self.getPromiseResult(self.promise_name)
    last_message = result['result']['message'].split('\n')[-1]
    self.assertEqual(result['result']['failed'], True)
    self.assertEqual(last_message, "FAILED: IPv4 reachable, IPv6 unreachable")

if __name__ == '__main__':
  unittest.main()
