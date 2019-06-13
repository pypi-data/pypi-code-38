# -*- coding: utf-8 -*-
import os, time
import sys
import shutil
import tempfile
import unittest
import json
from datetime import datetime
from slapos.monitor.runpromise import MonitorPromiseLauncher, getArgumentParser
from slapos.grid.promise.generic import PROMISE_LOG_FOLDER_NAME, PROMISE_RESULT_FOLDER_NAME

class MonitorPromiseTest(unittest.TestCase):

  def setUp(self):
    self.base_dir = tempfile.mkdtemp()
    self.etc_dir = os.path.join(self.base_dir, 'etc')
    self.output_dir = os.path.join(self.base_dir, PROMISE_RESULT_FOLDER_NAME)
    self.log_output_dir = os.path.join(self.base_dir, PROMISE_LOG_FOLDER_NAME)
    self.promise_dir = os.path.join(self.etc_dir, 'plugin')
    self.old_promise_dir = os.path.join(self.etc_dir, 'promise')
    self.public_dir = os.path.join(self.base_dir, 'public')
    self.private_dir = os.path.join(self.base_dir, 'private')
    self.run_dir = os.path.join(self.base_dir, 'run')
    self.log_dir = os.path.join(self.base_dir, 'log')
    os.mkdir(self.etc_dir)
    os.mkdir(self.promise_dir)
    os.mkdir(self.public_dir)
    os.mkdir(self.private_dir)
    os.mkdir(self.run_dir)
    os.mkdir(self.old_promise_dir)
    os.mkdir(self.log_dir)

    self.monitor_config = """[monitor]
private-folder = %(base_dir)s/private
public-folder = %(base_dir)s/public
root-title = %(root_title)s
log-folder = %(base_dir)s/log
base-url = %(base_url)s
title = %(title)s

[promises]
pid-path = %(base_dir)s/run/promises.pid
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
""" % {'base_dir': self.base_dir, 'title': 'Monitor', 'root_title': 'Monitor ROOT',
       'base_url': 'https://monitor.test.com', }

    self.monitor_config_file = os.path.join(self.base_dir, 'monitor.conf')
    with open(self.monitor_config_file, 'w') as f:
      f.write(self.monitor_config)

  def tearDown(self):
    if os.path.exists(self.base_dir):
      shutil.rmtree(self.base_dir)

  def writePromiseOK(self, name):
    content = """#!/bin/sh

echo "success"
exit 0
"""
    promise_path = os.path.join(self.old_promise_dir, name)
    self.writeContent(promise_path, content)
    os.chmod(promise_path, 0755)
    return promise_path

  def writePromiseNOK(self, name):
    content = """#!/bin/sh

echo "failed"
exit 2
"""
    promise_path = os.path.join(self.old_promise_dir, name)
    self.writeContent(promise_path, content)
    os.chmod(promise_path, 0755)
    return promise_path

  def generatePromiseScript(self, name, success=True, failure_count=1, content="",
      periodicity=0.03):
    promise_content = """from zope import interface as zope_interface
from slapos.grid.promise import interface
from slapos.grid.promise import GenericPromise

class RunPromise(GenericPromise):

 zope_interface.implements(interface.IPromise)

 def __init__(self, config):
   GenericPromise.__init__(self, config)
   self.setPeriodicity(minute=%(periodicity)s)

 def sense(self):
   %(content)s

   if not %(success)s:
     self.logger.error("failed")
   else:
     self.logger.info("success")

 def anomaly(self):
   return self._anomaly(result_count=2, failure_amount=%(failure_amount)s)

 def test(self):
   return self._test(result_count=1, failure_amount=%(failure_amount)s)
""" % {'success': success, 'content': content, 'failure_amount': failure_count,
      'periodicity': periodicity}
 
    with open(os.path.join(self.promise_dir, name), 'w') as f:
      f.write(promise_content)
    return os.path.join(self.promise_dir, name)

  def writeContent(self, file_path, config):
    with open(file_path, 'w') as cfg:
      cfg.write(config)

  def getPromiseParser(self, use_config=True, check_anomaly=False, force=False):

    arg_parser = getArgumentParser()
    base_list = ['-c', self.monitor_config_file]
    if use_config:
      if check_anomaly:
        base_list.append('-a')
      if force:
        base_list.append('--force')
      return arg_parser.parse_args(base_list)

    pid_path = os.path.join(self.run_dir, 'monitor-promise.pid')
    promise_cmd = [
      '--pid-path',
      '%s' % pid_path, '-o', self.public_dir,
      '--master-url', 'http://10.0.151.118:50000',
      '--partition-id', 'slappart0',
      '--computer-id', 'COMP-1234']
    return arg_parser.parse_args(promise_cmd)

  def test_promise_generic(self):
    promise_file = self.generatePromiseScript('my_promise.py', success=True)
    promise_file2 = self.generatePromiseScript('my_second_promise.py', success=True)
    parser = self.getPromiseParser()
    promise_runner = MonitorPromiseLauncher(parser)
    promise_runner.start()

    result_file = os.path.join(self.output_dir, 'my_promise.status.json')
    os.system('cat %s' % result_file)
    self.assertTrue(os.path.exists(result_file))
    my_result = json.loads(open(result_file).read().decode("utf-8"))
    my_result['result'].pop('date')
    expected_result = {
      u'title': u'my_promise', u'name': u'my_promise.py',
      u'result': {
        u'failed': False, u'message': u'success', u'type': u'Test Result'
        },
      u'execution-time': 0.05,
      u'path': u'%s/my_promise.py' % self.promise_dir,
    }
    self.assertEqual(expected_result, my_result)

    result_file = os.path.join(self.output_dir, 'my_second_promise.status.json')
    self.assertTrue(os.path.exists(result_file))
    second_result = json.loads(open(result_file).read().decode("utf-8"))
    second_result['result'].pop('date')

    expected_result = {
      u'title': u'my_second_promise', u'name': u'my_second_promise.py',
      u'result': {
        u'failed': False, u'message': u'success', u'type': u'Test Result'
        },
      u'execution-time': 0.05,
      u'path': u'%s/my_second_promise.py' % self.promise_dir,
    }
    self.assertEqual(expected_result, second_result)

  def test_promise_generic_failed(self):
    promise_file = self.generatePromiseScript('my_promise.py', success=False)
    parser = self.getPromiseParser()
    promise_runner = MonitorPromiseLauncher(parser)
    promise_runner.start()

    result_file = os.path.join(self.output_dir, 'my_promise.status.json')
    self.assertTrue(os.path.exists(result_file))
    my_result = json.loads(open(result_file).read().decode("utf-8"))
    my_result['result'].pop('date')

    expected_result = {
      u'title': u'my_promise', u'name': u'my_promise.py',
      u'result': {
        u'failed': True, u'message': u'failed', u'type': u'Test Result'
        },
      u'execution-time': 0.05,
      u'path': u'%s/my_promise.py' % self.promise_dir,
    }
    self.assertEqual(expected_result, my_result)

  def test_promise_generic_status_change(self):
    promise_file = self.generatePromiseScript('my_promise.py', success=False)
    parser = self.getPromiseParser()
    promise_runner = MonitorPromiseLauncher(parser)
    promise_runner.start()

    result_file = os.path.join(self.output_dir, 'my_promise.status.json')
    self.assertTrue(os.path.exists(result_file))
    my_result = json.loads(open(result_file).read().decode("utf-8"))
    my_result['result'].pop('date')

    expected_result = {
      u'title': u'my_promise', u'name': u'my_promise.py',
      u'result': {
        u'failed': True, u'message': u'failed', u'type': u'Test Result'
        },
      u'execution-time': 0.05,
      u'path': u'%s/my_promise.py' % self.promise_dir,
    }
    self.assertEqual(expected_result, my_result)

    os.system('rm %s/*.pyc' % self.promise_dir)
    time.sleep(2)
    self.generatePromiseScript('my_promise.py', success=True)
    promise_runner2 = MonitorPromiseLauncher(parser)
    promise_runner2.start()

    my_result = json.loads(open(result_file).read().decode("utf-8"))
    my_result['result'].pop('date')

    expected_result = {
      u'title': u'my_promise', u'name': u'my_promise.py',
      u'result': {
        u'failed': False, u'message': u'success', u'type': u'Test Result'
        },
      u'execution-time': 0.05,
      u'path': u'%s/my_promise.py' % self.promise_dir,
    }
    self.assertEqual(expected_result, my_result)

  def test_promise_generic_periodicity(self):
    promise_file = self.generatePromiseScript('my_promise.py', success=False, periodicity=0.03)
    parser = self.getPromiseParser()
    promise_runner = MonitorPromiseLauncher(parser)
    promise_runner.start()

    result_file = os.path.join(self.output_dir, 'my_promise.status.json')
    self.assertTrue(os.path.exists(result_file))

    # run again
    os.unlink(result_file)
    promise_runner = MonitorPromiseLauncher(parser)
    promise_runner.start()
    self.assertFalse(os.path.exists(result_file))

    time.sleep(2)
    promise_runner = MonitorPromiseLauncher(parser)
    promise_runner.start()
    self.assertTrue(os.path.exists(result_file))

  def test_promise_generic_run_only(self):
    promise_file = self.generatePromiseScript('my_promise.py', success=False)
    second_promise = self.generatePromiseScript('my_second_promise.py', success=False)
    parser = self.getPromiseParser()
    promise_runner = MonitorPromiseLauncher(parser)
    promise_runner.start()

    result_file = os.path.join(self.output_dir, 'my_promise.status.json')
    second_result = os.path.join(self.output_dir, 'my_second_promise.status.json')
    self.assertTrue(os.path.exists(result_file))
    self.assertTrue(os.path.exists(second_result))

    config = getArgumentParser().parse_args(['-c', self.monitor_config_file, '-a', '-f',
                                      '--run-only', 'my_second_promise.py'])
    os.unlink(result_file)
    promise_runner = MonitorPromiseLauncher(config)
    promise_runner.start()
    self.assertFalse(os.path.exists(result_file))
    self.assertTrue(os.path.exists(second_result))

  def test_promise_OK(self):
    promise = self.writePromiseOK('promise_1')
    parser = self.getPromiseParser()
    promise_runner = MonitorPromiseLauncher(parser)
    promise_runner.start()

    result_file = os.path.join(self.output_dir, 'promise_1.status.json')
    self.assertTrue(os.path.exists(result_file))
    result1 = json.loads(open(result_file).read().decode("utf-8"))
    start_date = datetime.strptime(result1['result'].pop('date'), '%Y-%m-%dT%H:%M:%S+0000')

    expected_result = {
      u'title': u'promise_1', u'name': u'promise_1',
      u'result': {
        u'failed': False, u'message': u'success', u'type': u'Test Result'
        },
      u'execution-time': 0.05,
      u'path': u'%s' % promise,
    }

    # second run
    parser = self.getPromiseParser(force=True)
    promise_runner = MonitorPromiseLauncher(parser)
    promise_runner.start()
    result2 = json.loads(open(result_file).read().decode("utf-8"))
    start_date2 = datetime.strptime(result2['result'].pop('date'), '%Y-%m-%dT%H:%M:%S+0000')
    self.assertEqual(expected_result, result2)

  def test_promise_two_folder(self):

    promise = self.writePromiseOK('promise_1')
    promise2 = self.writePromiseOK('promise_2')
    parser = self.getPromiseParser()
    promise_runner = MonitorPromiseLauncher(parser)
    promise_runner.start()

    result_file = os.path.join(self.output_dir, 'promise_1.status.json')
    result2_file = os.path.join(self.output_dir, 'promise_2.status.json')
    self.assertTrue(os.path.exists(result_file))
    self.assertTrue(os.path.exists(result2_file))
    result1 = json.loads(open(result_file).read().decode("utf-8"))
    start_date = datetime.strptime(result1['result'].pop('date'), '%Y-%m-%dT%H:%M:%S+0000')

    expected_result = {
      u'title': u'promise_1', u'name': u'promise_1',
      u'result': {
        u'failed': False, u'message': u'success', u'type': u'Test Result'
        },
      u'execution-time': 0.05,
      u'path': u'%s' % promise,
    }
    self.assertEqual(expected_result, result1)

    result2 = json.loads(open(result2_file).read())
    start_date2 = datetime.strptime(result2['result'].pop('date'), '%Y-%m-%dT%H:%M:%S+0000')

    expected_result = {
      u'title': u'promise_2', u'name': u'promise_2',
      u'result': {
        u'failed': False, u'message': u'success', u'type': u'Test Result'
        },
      u'execution-time': 0.05,
      u'path': u'%s' % promise2,
    }
    self.assertEqual(expected_result, result2)

  def test_promise_NOK(self):
    promise = self.writePromiseNOK('promise_1')
    parser = self.getPromiseParser()
    promise_runner = MonitorPromiseLauncher(parser)
    promise_runner.start()

    result_file = os.path.join(self.output_dir, 'promise_1.status.json')
    self.assertTrue(os.path.exists(result_file))
    result1 = json.loads(open(result_file).read().decode("utf-8"))
    result1['result'].pop('date')
    expected_result = {
      u'title': u'promise_1', u'name': u'promise_1',
      u'result': {
        u'failed': True, u'message': u'failed', u'type': u'Test Result'
        },
      u'execution-time': 0.05,
      u'path': u'%s' % promise,
    }
    self.assertEqual(expected_result, result1)

    # second run
    promise_runner = MonitorPromiseLauncher(parser)
    promise_runner.start()
    result2 = json.loads(open(result_file).read().decode("utf-8"))
    result2['result'].pop('date')
    self.assertEqual(expected_result, result2)

  def test_promise_mixed(self):
    promise = self.writePromiseOK('promise_1')
    parser = self.getPromiseParser()
    promise_runner = MonitorPromiseLauncher(parser)
    promise_runner.start()

    result_file = os.path.join(self.output_dir, 'promise_1.status.json')
    self.assertTrue(os.path.exists(result_file))
    result1 = json.loads(open(result_file).read().decode("utf-8"))
    result1['result'].pop('date')
    expected_result = {
      u'title': u'promise_1', u'name': u'promise_1',
      u'result': {
        u'failed': False, u'message': u'success', u'type': u'Test Result'
        },
      u'execution-time': 0.05,
      u'path': u'%s' % promise,
    }
    self.assertEqual(expected_result, result1)

    # second run with failure
    time.sleep(1)
    promise = self.writePromiseNOK('promise_1')
    parser = self.getPromiseParser(force=True)
    expected_result['result']['message'] = u'failed'
    expected_result['result']['failed'] = True
    promise_runner = MonitorPromiseLauncher(parser)
    promise_runner.start()

    result2 = json.loads(open(result_file).read().decode("utf-8"))
    result2['result'].pop('date')
    self.assertEqual(expected_result, result2)

