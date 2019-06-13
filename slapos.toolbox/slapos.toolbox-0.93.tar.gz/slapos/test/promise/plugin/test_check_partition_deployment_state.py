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

class TestPartitionDeploymentState(TestPromisePluginMixin):

  def setUp(self):
    TestPromisePluginMixin.setUp(self)
    log_folder = os.path.join(self.partition_dir, 'var/log')
    os.makedirs(log_folder)

  def writeState(self, message):
    path = os.path.join(self.partition_dir, '.slapgrid-%s-error.log' % self.partition_id)
    with open(path, 'w') as f:
      f.write(message)

  def test_partition_deployment_state_ok(self):
    content = """
from slapos.promise.plugin.check_partition_deployment_state import RunPromise
"""
    self.writePromise("partition-deployment-state.py", content)
    self.configureLauncher()
    self.launcher.run()
    result = self.getPromiseResult("partition-deployment-state.py")
    self.assertEqual(result['result']['failed'], False)
    self.assertEqual(result['result']['message'], 'buildout is OK')

  def test_partition_deployment_state_failed(self):
    content = """
from slapos.promise.plugin.check_partition_deployment_state import RunPromise
"""
    message = "Slapgrid failed to process partition XXXXXXX"
    self.writePromise("partition-deployment-state.py", content)
    self.writeState(message)
    self.configureLauncher()
    with self.assertRaises(PromiseError):
      self.launcher.run()
    result = self.getPromiseResult("partition-deployment-state.py")
    buildout_output = os.path.join(self.partition_dir, 'var/log', 'slapgrid-%s-error.log' % self.partition_id)

    self.assertEqual(result['result']['failed'], True)
    self.assertEqual(result['result']['message'], 'Buildout failed to process %s.' % self.partition_id)
    with open(buildout_output) as f:
      self.assertEqual(f.read(), message)

if __name__ == '__main__':
  unittest.main()
