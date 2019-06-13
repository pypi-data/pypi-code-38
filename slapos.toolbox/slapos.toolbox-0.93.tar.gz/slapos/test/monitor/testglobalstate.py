# -*- coding: utf-8 -*-
import os, time
import sys
import shutil
import tempfile
import unittest
import json
import pkg_resources

from slapos.monitor import globalstate
from slapos.monitor.runpromise import MonitorPromiseLauncher, getArgumentParser
from slapos.monitor.monitor import Monitoring
from jsonschema import validate

class MonitorGlobalTest(unittest.TestCase):

  def setUp(self):
    self.base_dir = tempfile.mkdtemp()
    self.etc_dir = os.path.join(self.base_dir, 'etc')
    self.output_dir = os.path.join(self.base_dir, '.slapgrid/promise/result')
    os.mkdir(self.etc_dir)
    os.mkdir(os.path.join(self.etc_dir, 'plugin'))
    os.mkdir(os.path.join(self.etc_dir, 'promise'))
    os.mkdir(os.path.join(self.base_dir, 'public'))
    os.mkdir(os.path.join(self.base_dir, 'private'))
    os.mkdir(os.path.join(self.base_dir, 'cron.d'))
    os.mkdir(os.path.join(self.base_dir, 'log'))
    os.mkdir(os.path.join(self.base_dir, 'log-backup'))
    os.mkdir(os.path.join(self.base_dir, 'logrotate.d'))
    os.mkdir(os.path.join(self.base_dir, 'monitor-report'))
    os.mkdir(os.path.join(self.base_dir, 'webdav'))
    os.mkdir(os.path.join(self.base_dir, 'run'))
    os.mkdir(os.path.join(self.base_dir, 'private/documents'))
    self.writeContent(os.path.join(self.base_dir, 'param'), '12345')
    self.writeContent(os.path.join(self.base_dir, '.monitor_pwd'), 'bcuandjy')
    self.writeContent(os.path.join(self.base_dir, 'test-httpd-cors.cfg'), '')
    self.writeContent(os.path.join(self.base_dir, 'monitor-htpasswd'), '12345')

    self.monitor_config_file = os.path.join(self.base_dir, 'monitor.conf')
    self.public_dir = os.path.join(self.base_dir, 'public')
    self.private_dir = os.path.join(self.base_dir, 'private')

    monitor_schema_string = \
      pkg_resources.resource_string(
        'slapos.monitor',
        'doc/monitor_instance.schema.json')
    self.monitor_instance_schema = json.loads(monitor_schema_string)


    self.monitor_config_dict = dict(
      monitor_conf=self.monitor_config_file,
      base_dir=self.base_dir,
      root_title="Monitor ROOT",
      title="Monitor",
      url_list="https://sub.monitor.test.com https://sub2.monitor.test.com",
      base_url="https://monitor.test.com",
      etc_dir=self.etc_dir,
      promise_runner_pid=os.path.join(self.base_dir, 'run', 'monitor-promises.pid'),
      public_folder=os.path.join(self.base_dir, 'public'),
      public_path_list="",
      private_path_list="",
      promise_run_script="/bin/echo",
      collect_run_script="/bin/echo",
      statistic_script="/bin/echo"
    )
    self.monitor_conf = """[monitor]
parameter-file-path = %(base_dir)s/knowledge0.cfg
service-pid-folder = %(base_dir)s/run
private-folder = %(base_dir)s/private
public-folder = %(base_dir)s/public
public-path-list = %(public_path_list)s
private-path-list = %(private_path_list)s
crond-folder = %(base_dir)s/cron.d
logrotate-folder = %(base_dir)s/logrotate.d
root-title = %(root_title)s
pid-file =  %(base_dir)s/monitor.pid
log-folder = %(base_dir)s/log
log-backup-folder = %(base_dir)s/log-backup
document-folder = %(base_dir)s/private/documents
parameter-list = 
  raw monitor-user admin
  file sample %(base_dir)s/param
  htpasswd monitor-password %(base_dir)s/.monitor_pwd admin %(base_dir)s/monitor-htpasswd
  httpdcors cors-domain %(base_dir)s/test-httpd-cors.cfg /bin/echo

webdav-folder = %(base_dir)s/webdav
collect-script = %(collect_run_script)s
statistic-script = %(statistic_script)s
python = python
monitor-url-list = %(url_list)s
collector-db = 
base-url = %(base_url)s
title = %(title)s
service-pid-folder = %(base_dir)s/run
promise-output-file = %(base_dir)s/monitor-bootstrap-status
promise-runner = %(promise_run_script)s
randomsleep = /bin/echo sleep

[promises]
output-folder = %(base_dir)s/public
legacy-promise-folder = %(etc_dir)s/promise
promise-folder = %(etc_dir)s/plugin
partition-folder = %(base_dir)s
computer-id = COMP-1234
partition-cert = 
partition-key = 
partition-id = slappart0
ipv6 = 2001:34c:1254:df3:89::5df3
software-release = http://some.url.com/software.cfg
master-url = http://10.0.151.118:50000
software-type = default
ipv4 = 10.0.151.118
"""

  def tearDown(self):
    if os.path.exists(self.base_dir):
      shutil.rmtree(self.base_dir)

  def writeContent(self, file_path, config):
    with open(file_path, 'w') as cfg:
      cfg.write(config)

  def writePromise(self, name, success=True):
    if success:
      result_dict = {'output': 'success', 'code': 0}
    else:
      result_dict = {'output': 'error', 'code': 1}
    content = """#!/bin/sh

echo "%(output)s"
exit %(code)s
""" % result_dict
    promise_path = os.path.join(self.etc_dir, 'promise', name)
    self.writeContent(promise_path, content)
    os.chmod(promise_path, 0755)
    return promise_path

  def getPromiseParser(self):
    pid_path = os.path.join(self.base_dir, 'run', 'monitor-promise.pid')

    promise_cmd = [
      '--pid-path',
      '%s' % pid_path, '-c', self.monitor_config_file]
    arg_parser = getArgumentParser()
    return arg_parser.parse_args(promise_cmd)

  def test_monitor_instance_state(self):
    self.maxDiff = None
    config_content = self.monitor_conf % self.monitor_config_dict
    self.writeContent(self.monitor_config_file, config_content)

    instance = Monitoring(self.monitor_config_file)
    instance.bootstrapMonitor()

    self.writePromise('promise_1')
    self.writePromise('promise_2', success=False)
    self.writePromise('promise_3', success=False)
    self.writePromise('promise_4')
    parser = self.getPromiseParser()
    promise_runner = MonitorPromiseLauncher(parser)
    promise_runner.start()

    self.assertTrue(os.path.exists(os.path.join(self.output_dir, 'promise_1.status.json')))
    self.assertTrue(os.path.exists(os.path.join(self.output_dir, 'promise_2.status.json')))
    self.assertTrue(os.path.exists(os.path.join(self.output_dir, 'promise_3.status.json')))
    self.assertTrue(os.path.exists(os.path.join(self.output_dir, 'promise_4.status.json')))

    os.symlink(self.output_dir, '%s/public/promise' % self.base_dir)
    # generate instance state files
    globalstate.run(self.monitor_config_file)
    self.assertTrue(os.path.exists(os.path.join(self.public_dir, 'feed')))
    self.assertTrue(os.path.exists(os.path.join(self.public_dir, 'monitor.global.json')))
    self.assertTrue(os.path.exists(os.path.join(self.private_dir, 'monitor.global.json')))
    expected_result = """{
	"status": "ERROR",
	"partition_id": "slappart0",
	"ipv6": "2001:34c:1254:df3:89::5df3",
	"ipv4": "10.0.151.118",
	"software_release": "http://some.url.com/software.cfg",
	"software_type": "default",
	"parameters": [{
		"key": "",
		"value": "admin",
		"title": "monitor-user"
	}, {
		"key": "sample",
		"value": "12345",
		"title": "sample"
	}, {
		"key": "monitor-password",
		"value": "bcuandjy",
		"title": "monitor-password"
	}, {
		"key": "cors-domain",
		"value": "",
		"title": "cors-domain"
	}],
	"title": "Monitor",
	"data": {
		"process_state": "monitor_process_resource.status",
		"io_resource": "monitor_resource_io.data",
		"state": "monitor_state.data",
		"memory_resource": "monitor_resource_memory.data",
		"process_resource": "monitor_resource_process.data",
		"monitor_process_state": "monitor_resource.status"
	},
	"portal_type": "Software Instance",
	"state": {
		"success": 2,
		"error": 2
	},
	"_links": {
		"rss_url": {
			"href": "https://monitor.test.com/public/feed"
		},
		"public_url": {
			"href": "https://monitor.test.com/share/public/"
		},
		"private_url": {
			"href": "https://monitor.test.com/share/private/"
		},
		"related_monitor": [
		  {"href": "https://sub.monitor.test.com/share/public"},
      {"href": "https://sub2.monitor.test.com/share/public"}
    ]
	},
	"aggregate_reference": "COMP-1234",
	"type": "global",
	"specialise_title": "Monitor ROOT"
}"""

    with open(os.path.join(self.private_dir, 'monitor.global.json')) as r:
      result = json.loads(r.read().decode("utf-8"))
      result.pop("date")
      self.assertEqual(result,
        json.loads(expected_result))

    # all promises are OK now
    self.writePromise('promise_2', success=True)
    self.writePromise('promise_3', success=True)
    # rerun right now
    promise_runner.config.force = True
    promise_runner.start()
    globalstate.run(self.monitor_config_file)

    expected_result_dict = json.loads(expected_result)
    expected_result_dict["status"] = "OK"
    expected_result_dict["state"] = {'error': 0, 'success': 4}
    instance_result_dict = None
    with open(os.path.join(self.private_dir, 'monitor.global.json')) as r:
      instance_result_dict = json.loads(r.read().decode("utf-8"))
      result = instance_result_dict.copy()
      result.pop("date")
      self.assertEqual(result,
        expected_result_dict)

    # validate returned json result
    validate(instance_result_dict, self.monitor_instance_schema)

