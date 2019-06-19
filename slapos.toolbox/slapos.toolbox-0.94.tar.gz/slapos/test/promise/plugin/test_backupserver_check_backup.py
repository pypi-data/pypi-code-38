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
from datetime import datetime,timedelta

class TestBackupserverCheckBackup(TestPromisePluginMixin):

  def setUp(self):
    TestPromisePluginMixin.setUp(self)
    log_folder = os.path.join(self.partition_dir, 'var/log')
    os.makedirs(log_folder)

    self.status_name = 'SOFTINSTTEST_status.txt'
    self.status_fullpath = os.path.join(log_folder, self.status_name)
    self.cron_frequency = '0 0 * * *'

    self.promise_name = "backupserver_check_backup.py"

    content = """from slapos.promise.plugin.backupserver_check_backup import RunPromise


extra_config_dict = {{
  'cron_frequency': '{}',
  'statistic_dirbasename': 'DUMMY_STATISTIC_DIRBASENAME',
  'statistic_name': 'DUMMY_STATISTIC_NAME',
  'status_dirbasename': 'DUMMY_STATUS_DIRBASENAME',
  'status_fullpath': '{}',
  'status_name': '{}',
  'monitor_url': 'https://DUMMY_MONITOR_URL',
}}
""".format(self.cron_frequency, self.status_fullpath, self.status_name)
    self.writePromise(self.promise_name, content)

  def tearDown(self):
    TestPromisePluginMixin.tearDown(self)
    if os.path.exists(self.status_fullpath):
      os.remove(self.status_fullpath)

  def format_status(self, date, status):
    """" return a string formatted like backupserver status """
    if date.tzinfo is not None:
      raise "Date should be UTC"
    return "{}+0000, DUMMY_STATISTIC_NAME, SOFTINSTTEST, backup {}\n".format(date.replace(microsecond=0).isoformat(), status)

  def test_check_backup_ok(self):
    now = datetime.utcnow()
    with open(self.status_fullpath, 'w') as f:
      f.write(self.format_status(now, "running"))
      f.write(self.format_status(now, "success"))

    self.configureLauncher(enable_anomaly=True)
    self.launcher.run()
    result = self.getPromiseResult(self.promise_name)
    self.assertEqual(result['result']['failed'], False)
    self.assertIn("Backup OK", result['result']['message'])

  def test_check_backup_fail(self):
    now = datetime.utcnow()
    with open(self.status_fullpath, 'w') as f:
      f.write(self.format_status(now, "running"))
      f.write(self.format_status(now, "failed"))

    self.configureLauncher(enable_anomaly=True)
    with self.assertRaises(PromiseError):
      self.launcher.run()
    result = self.getPromiseResult(self.promise_name)
    self.assertIn("Backup FAILED", result['result']['message'])

  def test_check_backup_too_long(self):
    now = datetime.utcnow()
    long_ago = now - timedelta(days = 2)
    with open(self.status_fullpath, 'w') as f:
      f.write(self.format_status(long_ago, "running"))

    self.configureLauncher(enable_anomaly=True)
    with self.assertRaises(PromiseError):
      self.launcher.run()
    result = self.getPromiseResult(self.promise_name)
    self.assertEqual(result['result']['failed'], True)
    self.assertIn("Backup didn't start at correct time", result['result']['message'])

if __name__ == '__main__':
  unittest.main()
