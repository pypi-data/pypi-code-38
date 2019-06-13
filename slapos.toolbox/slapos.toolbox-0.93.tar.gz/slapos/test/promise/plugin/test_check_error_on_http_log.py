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
import os
import time
from slapos.test.promise import data
from slapos.grid.promise import PromiseError

class TestCheckErrorOnHttpLog(TestPromisePluginMixin):

  def get_time(self, sec):
    return time.strftime("%a %b %d %H:%M:%S %Y", time.localtime(time.time()-sec))

  def _update_logs(self):
    log_file_list = [
       "apache_error_log",
       "infoonly_error_log",
       "timeout_error_log",
       "unreachable_error_log"]
    i = 600
    for log_file in log_file_list:
      new = ""
      old = ""
      with open(self.base_path + "/" + log_file) as f:
        for line in f:
          new += line.replace("DATETIME", self.get_time(i))
          old += line.replace("DATETIME", self.get_time(i+3600))
          i -= 1

      with open(self.base_path + "/SOFTINST-0_" + log_file, "w") as f:
        f.write(old)
        f.write(new)

  def setUp(self):
    TestPromisePluginMixin.setUp(self)
    log_folder = os.path.join(self.partition_dir, 'var/log')
    os.makedirs(log_folder)

    self.base_path = "/".join(data.__file__.split("/")[:-1])
    self._update_logs()

    self.promise_name = "check-error-on-apache-log.py"
    self.promise_pyc = os.path.join(self.plugin_dir, self.promise_name + "c")

    self.base_content = """from slapos.promise.plugin.check_error_on_http_log import RunPromise

extra_config_dict = {
  'log-file': '%(log_file)s',
  'maximum-delay': '%(maximum_delay)s',
}
"""

  def tearDown(self):
    TestPromisePluginMixin.tearDown(self)

  def test_no_error(self):
    self.base_path = "/".join(data.__file__.split("/")[:-1])
    content = self.base_content % {
      'log_file': self.base_path + "/SOFTINST-0_infoonly_error_log",
      'maximum_delay': 0
    }
    self.writePromise(self.promise_name, content)

    self.configureLauncher(force=True, enable_anomaly=True)
    self.launcher.run()
    # run a second time to add more results
    self.launcher.run()
    result = self.getPromiseResult(self.promise_name)
    self.assertEqual(result['result']['failed'], False)
    self.assertEqual(result['result']['message'], "OK")

    content = self.base_content % {
      'log_file': self.base_path + "/SOFTINST-0_infoonly_error_log",
      'maximum_delay': 3600
    }
    self.writePromise(self.promise_name, content)

    # remove previous pyc, so modified promise file will be used
    if os.path.exists(self.promise_pyc):
      os.unlink(self.promise_pyc)
    # Ignore periodicity of the promise
    self.launcher.run()
    result = self.getPromiseResult(self.promise_name)
    self.assertEqual(result['result']['failed'], False)
    self.assertEqual(result['result']['message'], "OK")

  def test_error(self):
    self.base_path = "/".join(data.__file__.split("/")[:-1])
    content = self.base_content % {
      'log_file': self.base_path + "/SOFTINST-0_apache_error_log",
      'maximum_delay': 0
    }
    self.writePromise(self.promise_name, content)

    self.configureLauncher(force=True, enable_anomaly=True)
    self.launcher.run()
    with self.assertRaises(PromiseError):
      self.launcher.run()
    result = self.getPromiseResult(self.promise_name)
    self.assertEqual(result['result']['failed'], True)
    self.assertEqual(result['result']['message'], "ERROR=2 (NOROUTE=2, UNREACHABLENET=0, TIMEOUT=0)")

    content = self.base_content % {
      'log_file': self.base_path + "/SOFTINST-0_apache_error_log",
      'maximum_delay': 3600
    }
    self.writePromise(self.promise_name, content)

    # remove previous pyc, so modified promise file will be used
    if os.path.exists(self.promise_pyc):
      os.unlink(self.promise_pyc)
    # Ignore periodicity of the promise
    with self.assertRaises(PromiseError):
      self.launcher.run()
    result = self.getPromiseResult(self.promise_name)
    self.assertEqual(result['result']['failed'], True)
    self.assertEqual(result['result']['message'], "ERROR=1 (NOROUTE=1, UNREACHABLENET=0, TIMEOUT=0)")

  def test_error_timeout(self):
    self.base_path = "/".join(data.__file__.split("/")[:-1])
    content = self.base_content % {
      'log_file': self.base_path + "/SOFTINST-0_timeout_error_log",
      'maximum_delay': 0
    }
    self.writePromise(self.promise_name, content)

    self.configureLauncher(force=True, enable_anomaly=True)
    self.launcher.run()
    with self.assertRaises(PromiseError):
      self.launcher.run()
    result = self.getPromiseResult(self.promise_name)
    self.assertEqual(result['result']['failed'], True)
    self.assertEqual(result['result']['message'], "ERROR=4 (NOROUTE=0, UNREACHABLENET=0, TIMEOUT=4)")

    content = self.base_content % {
      'log_file': self.base_path + "/SOFTINST-0_timeout_error_log",
      'maximum_delay': 3600
    }
    self.writePromise(self.promise_name, content)

    # remove previous pyc, so modified promise file will be used
    if os.path.exists(self.promise_pyc):
      os.unlink(self.promise_pyc)
    # Ignore periodicity of the promise
    with self.assertRaises(PromiseError):
      self.launcher.run()
    result = self.getPromiseResult(self.promise_name)
    self.assertEqual(result['result']['failed'], True)
    self.assertEqual(result['result']['message'], "ERROR=2 (NOROUTE=0, UNREACHABLENET=0, TIMEOUT=2)")

  def test_error_unreacheabler(self):
    self.base_path = "/".join(data.__file__.split("/")[:-1])
    content = self.base_content % {
      'log_file': self.base_path + "/SOFTINST-0_unreachable_error_log",
      'maximum_delay': 0
    }
    self.writePromise(self.promise_name, content)

    self.configureLauncher(force=True, enable_anomaly=True)
    self.launcher.run()
    with self.assertRaises(PromiseError):
      self.launcher.run()
    result = self.getPromiseResult(self.promise_name)
    self.assertEqual(result['result']['failed'], True)
    self.assertEqual(result['result']['message'], "ERROR=11 (NOROUTE=0, UNREACHABLENET=11, TIMEOUT=0)")

    content = self.base_content % {
      'log_file': self.base_path + "/SOFTINST-0_unreachable_error_log",
      'maximum_delay': 3600
    }
    self.writePromise(self.promise_name, content)

    # remove previous pyc, so modified promise file will be used
    if os.path.exists(self.promise_pyc):
      os.unlink(self.promise_pyc)
    # Ignore periodicity of the promise
    with self.assertRaises(PromiseError):
      self.launcher.run()
    result = self.getPromiseResult(self.promise_name)
    self.assertEqual(result['result']['failed'], True)
    self.assertEqual(result['result']['message'], "ERROR=11 (NOROUTE=0, UNREACHABLENET=11, TIMEOUT=0)")

if __name__ == '__main__':
  unittest.main()
