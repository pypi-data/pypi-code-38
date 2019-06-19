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
import os, shutil
import tempfile
import unittest
import json
from slapos.grid.promise import PromiseLauncher
from slapos.grid.promise.generic import (PROMISE_RESULT_FOLDER_NAME,
                                         PROMISE_LOG_FOLDER_NAME)

class TestPromisePluginMixin(unittest.TestCase):

  def setUp(self):
    self.partition_dir = tempfile.mkdtemp()
    self.plugin_dir = os.path.join(self.partition_dir, 'plugin')
    self.legacy_promise_dir = os.path.join(self.partition_dir, 'promise')
    self.log_dir = os.path.join(self.partition_dir, 'log')
    os.mkdir(self.plugin_dir)
    os.mkdir(self.log_dir)
    os.makedirs('%s/%s' % (self.partition_dir, PROMISE_RESULT_FOLDER_NAME))
    os.makedirs('%s/%s' % (self.partition_dir, PROMISE_LOG_FOLDER_NAME))
    os.mkdir(self.legacy_promise_dir)
    self.partition_id = "slappart0"
    self.computer_id = "COMP-1234"

  def tearDown(self):
    if os.path.exists(self.partition_dir):
      shutil.rmtree(self.partition_dir)

  def configureLauncher(self, timeout=0.5, master_url="", debug=False,
      run_list=[], uid=None, gid=None, enable_anomaly=False, force=False,
      logdir=True, dry_run=False):
    parameter_dict = {
      'promise-timeout': timeout,
      'promise-folder': self.plugin_dir,
      'legacy-promise-folder': self.legacy_promise_dir,
      'log-folder': self.log_dir if logdir else None,
      'partition-folder': self.partition_dir,
      'master-url': master_url,
      'partition-cert': "",
      'partition-key': "",
      'partition-id': self.partition_id,
      'computer-id': self.computer_id,
      'debug': debug,
      'check-anomaly': enable_anomaly,
      'force': force,
      'run-only-promise-list': run_list,
      'uid': uid,
      'gid': gid
    }

    self.launcher = PromiseLauncher(
      config=parameter_dict,
      logger=None,
      dry_run=dry_run
    )


  def getPromiseResult(self, promise_name):
    title = os.path.splitext(promise_name)[0]
    result_path = os.path.join(self.partition_dir, PROMISE_RESULT_FOLDER_NAME, '%s.status.json' % title)

    with open(result_path) as f:
      return json.load(f)

  def writePromise(self, promise_name, content):
    with open(os.path.join(self.plugin_dir, promise_name), 'w') as f:
      f.write(content)
