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

class TestPromiseMonitorBoostrap(TestPromisePluginMixin):

  def setUp(self):
    TestPromisePluginMixin.setUp(self)
    self.pid_file = os.path.join(self.partition_dir, 'monitor.pid')
    self.state_file = os.path.join(self.partition_dir, 'monitor.state')
    self.promise_name = "my-monitor-bootstrap.py"

    content = """from slapos.promise.plugin.monitor_bootstrap_status import RunPromise

extra_config_dict = {
  'process-pid-file': "%(pid_file)s",
  'process-name': "monitor.boostrap",
  'status-file': "%(state_file)s",
}
""" % {'pid_file': self.pid_file, 'state_file': self.state_file}
    self.writePromise(self.promise_name, content)

    self.writeState("Buildout running...")

  def writeState(self, message):
    path = os.path.join(self.partition_dir, ".%s_%s.log" % (self.partition_id, "monitor.boostrap"))
    with open(path, 'w') as f:
      f.write(message)
    os.system('ls -l ' + path) 

  def writePid(self, pid):
    with open(self.pid_file, 'w') as f:
      f.write('%s' % pid)

  def writeResult(self, message):
    with open(self.state_file, 'w') as f:
      f.write(message)

  def test_monitor_bootstrap_no_run(self):
    self.configureLauncher()
    self.launcher.run()
    result = self.getPromiseResult(self.promise_name)
    self.assertEqual(result['result']['failed'], False)
    self.assertEqual(result['result']['message'], "Bootstrap didn't run!")

  def test_monitor_bootstrap_ok(self):
    self.writeResult('')
    self.writePid(2425)
    self.configureLauncher()
    self.launcher.run()
    result = self.getPromiseResult(self.promise_name)
    self.assertEqual(result['result']['failed'], False)
    self.assertEqual(result['result']['message'], "Bootstrap OK")

  def test_monitor_bootstrap_fail(self):
    self.writePid(2425)
    self.configureLauncher()
    with self.assertRaises(PromiseError):
      self.launcher.run()
    result = self.getPromiseResult(self.promise_name)
    self.assertEqual(result['result']['failed'], True)
    message = "Monitor bootstrap exited with error.\n ---- Latest monitor-boostrap.log ----\nBuildout running..."
    self.assertEqual(result['result']['message'], message)

if __name__ == '__main__':
  unittest.main()
