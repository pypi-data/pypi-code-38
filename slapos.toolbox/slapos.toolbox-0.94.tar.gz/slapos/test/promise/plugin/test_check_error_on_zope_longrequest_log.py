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
from slapos.test.promise import data
import time
from slapos.grid.promise import PromiseError


class TestCheckErrorOnZopeLongrequestLog(TestPromisePluginMixin):

  def setUp(self):
    TestPromisePluginMixin.setUp(self)
    self.promise_name = "check-error-on-zope_longrequest-log.py"
    self.base_path = "/".join(data.__file__.split("/")[:-1])
    self.log_file = self.base_path + "/longrequest_logger_zope.log"
    self.test_log_file = self.base_path + "/SOFTINST-0_longrequest_logger_zope.log"
    self._update_logs()

  def get_time(self, sec):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()-sec))

  def _update_logs(self):
    i = 600
    new = ""
    old = ""
    with open(self.log_file) as f:
      for line in f:
        new += line.replace("DATETIME", self.get_time(i))
        old += line.replace("DATETIME", self.get_time(i + 3600))
        i -= 1
      with open(self.test_log_file, "w") as f:
        f.write(old)
        f.write(new) 

  def test_01_no_delay_no_error_threshold(self):
    content = """from slapos.promise.plugin.check_error_on_zope_longrequest_log import RunPromise

extra_config_dict = {
  'log-file': '%(log_file)s',
  'error-threshold': 0,
  'maximum-delay': 0
}
""" % {'log_file': self.test_log_file}
    self.writePromise(self.promise_name, content)

    self.configureLauncher()
    with self.assertRaises(PromiseError):
      self.launcher.run()
    result = self.getPromiseResult(self.promise_name)
    self.assertEqual(result['result']['message'], "ERROR: Site has 6 long request")

  def test_02_no_delay_error_threshold(self):
    content = """from slapos.promise.plugin.check_error_on_zope_longrequest_log import RunPromise

extra_config_dict = {
  'log-file': '%(log_file)s',
  'error-threshold': 7,
  'maximum-delay': 0
}
""" % {'log_file': self.test_log_file}
    self.writePromise(self.promise_name, content)

    self.configureLauncher()
    self.launcher.run()
    result = self.getPromiseResult(self.promise_name)
    self.assertEqual(result['result']['message'], "INFO: Site has 6 long request")

  def test_03_delay_no_error_threshold(self):
    content = """from slapos.promise.plugin.check_error_on_zope_longrequest_log import RunPromise

extra_config_dict = {
  'log-file': '%(log_file)s',
  'error-threshold': 2,
  'maximum-delay': 3600
}
""" % {'log_file': self.test_log_file}
    self.writePromise(self.promise_name, content)
    self.configureLauncher()
    with self.assertRaises(PromiseError):
      self.launcher.run()
    result = self.getPromiseResult(self.promise_name)
    self.assertEqual(result['result']['message'], "ERROR: Site has 3 long request")


if __name__ == '__main__':
  unittest.main()
