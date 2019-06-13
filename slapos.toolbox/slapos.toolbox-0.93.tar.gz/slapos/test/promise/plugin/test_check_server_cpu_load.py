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

class TestCheckServerCPULoad(TestPromisePluginMixin):

  def setUp(self):
    TestPromisePluginMixin.setUp(self)
    self.promise_name = "server-cpu-load-promise.py"

    content = """from slapos.promise.plugin.check_server_cpu_load import RunPromise

extra_config_dict = {
  'cpu-load-threshold': '2.0',
}
"""
    self.writePromise(self.promise_name, content)

  def test_check_cpu_load_run(self):
    self.configureLauncher()
    self.launcher.run()
    result = self.getPromiseResult(self.promise_name)
    if result['result']['failed']:
      self.assertTrue("CPU load is high" in result['result']['message'])
    else:
      self.assertEqual("CPU load is OK", result['result']['message'].strip())

if __name__ == '__main__':
  unittest.main()
