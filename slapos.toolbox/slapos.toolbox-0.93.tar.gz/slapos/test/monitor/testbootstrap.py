# -*- coding: utf-8 -*-
import os, time
import sys
import shutil
import tempfile
import unittest
import json

from slapos.monitor.monitor import Monitoring

class MonitorBootstrapTest(unittest.TestCase):

  def setUp(self):
    self.base_dir = tempfile.mkdtemp()
    os.mkdir(os.path.join(self.base_dir, 'plugin'))
    os.mkdir(os.path.join(self.base_dir, 'promise'))
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

    self.monitor_config_dict = dict(
      monitor_conf=self.monitor_config_file,
      base_dir=self.base_dir,
      root_title="Monitor ROOT",
      title="Monitor",
      url_list="",
      base_url="https://monitor.test.com",
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
legacy-promise-folder = %(base_dir)s/promise
promise-folder = %(base_dir)s/plugin
partition-folder = %(base_dir)s
"""

    self.opml_outline = """<outline text="%(title)s" title="%(title)s" type="rss" version="RSS" htmlUrl="%(base_url)s/public/feed" xmlUrl="%(base_url)s/public/feed" url="%(base_url)s/share/private/" />"""

  def tearDown(self):
    if os.path.exists(self.base_dir):
      shutil.rmtree(self.base_dir)

  def writeContent(self, file_path, config):
    with open(file_path, 'w') as cfg:
      cfg.write(config)

  def configPromiseList(self, amount):
    promise_dir = os.path.join(self.base_dir, 'promise')
    plugin_dir = os.path.join(self.base_dir, 'plugin')
    promse_content = "/bin/bash echo something"
    for index in range(1, amount+1):
      promise_file = os.path.join(promise_dir, 'monitor_promise-%s' % index)
      self.writeContent(promise_file, promse_content)
      os.chmod(promise_file, 0755)
    for index in range(1, amount+1):
      promise_file = os.path.join(plugin_dir, 'monitor_promise-%s.py' % index)
      self.writeContent(promise_file, promse_content)
      os.chmod(promise_file, 0644)

  def checkOPML(self, url_list):
    opml_title = "<title>%(root_title)s</title>" % self.monitor_config_dict
    self.assertTrue(os.path.exists(os.path.join(self.base_dir, 'public/feeds')))

    with open(os.path.join(self.base_dir, 'public/feeds')) as f:
      opml_content = f.read()
      self.assertTrue(opml_title in opml_content)
      for url in url_list:
        opml_outline = self.opml_outline % dict(
          title=self.monitor_config_dict['title'],
          base_url=url)
      self.assertTrue(opml_outline in opml_content)

  def check_folder_equals(self, source, destination):
    self.assertTrue(os.path.isdir(source))

    if not destination.endswith('/'):
      destination += '/'
    dest_file_list = os.listdir(destination)
    source_file_list = os.listdir(source)
    self.assertEqual(dest_file_list, source_file_list)

  def check_symlink(self, source, destination):
    if source.endswith('/'):
      source.rstrip('/')
    if destination.endswith('/'):
      destination.rstrip('/')
    self.assertTrue(os.path.islink(destination))

    source_basename = os.path.basename(source)
    dest_basename = os.path.basename(destination)
    self.assertEqual(source_basename, dest_basename)

    if os.path.isdir(source):
      self.check_folder_equals(source, destination)

  def test_monitor_bootstrap_empty(self):
    config_content = self.monitor_conf % self.monitor_config_dict
    self.writeContent(self.monitor_config_file, config_content)

    instance = Monitoring(self.monitor_config_file)
    instance.bootstrapMonitor()
    promise_file = os.path.join(self.base_dir, 'monitor-bootstrap-status')
    self.assertTrue(os.path.exists(promise_file))

    self.checkOPML([self.monitor_config_dict['base_url']])

  def test_monitor_bootstrap_check_folder(self):

    folder_one = os.path.join(self.base_dir, 'folderOne')
    folder_two = os.path.join(self.base_dir, 'folderTwo')
    file_public = os.path.join(self.base_dir, 'file_public')
    private_one = os.path.join(self.base_dir, 'privateOne')
    private_two = os.path.join(self.base_dir, 'privateTwo')
    file_private = os.path.join(self.base_dir, 'file_private')

    os.mkdir(folder_one)
    os.mkdir(folder_two)
    os.mkdir(private_one)
    os.mkdir(private_two)

    self.writeContent(file_public, 'toto')
    self.writeContent(private_two+'/toto1', 'toto')
    self.writeContent(private_two+'/toto2', 'toto')
    self.writeContent(private_two+'/toto3', 'toto')
    self.writeContent(folder_two+'/toto1', 'toto')
    self.writeContent(folder_two+'/toto2', 'toto')
    self.writeContent(folder_two+'/toto3', 'toto')

    self.monitor_config_dict['public_path_list'] = '\n  '.join([
      folder_one,
      folder_two,
      file_public
    ])
    self.monitor_config_dict['private_path_list'] = '\n  '.join([
      private_one,
      private_two,
      file_private
    ])
    config_content = self.monitor_conf % self.monitor_config_dict
    self.writeContent(self.monitor_config_file, config_content)

    instance = Monitoring(self.monitor_config_file)
    instance.bootstrapMonitor()
    promise_file = os.path.join(self.base_dir, 'monitor-bootstrap-status')
    self.assertTrue(os.path.exists(promise_file))

    self.checkOPML([self.monitor_config_dict['base_url']])

    # check symlink configured
    self.check_symlink(folder_one, os.path.join(self.base_dir, 'public', 'folderOne'))
    self.check_symlink(folder_two, os.path.join(self.base_dir, 'public', 'folderTwo'))
    self.check_symlink(file_public, os.path.join(self.base_dir, 'public', 'file_public'))
    self.check_symlink(private_one, os.path.join(self.base_dir, 'private', 'privateOne'))
    self.check_symlink(private_two, os.path.join(self.base_dir, 'private', 'privateTwo'))
    self.check_symlink(file_private, os.path.join(self.base_dir, 'private', 'file_private'))

    # public and private folder are also accessible via webdav
    self.check_symlink(os.path.join(self.base_dir, 'public'),
      os.path.join(self.base_dir, 'webdav', 'public'))
    self.check_symlink(os.path.join(self.base_dir, 'private'),
      os.path.join(self.base_dir, 'webdav', 'private'))

    # check that configuration folder exist
    self.assertTrue(os.path.exists(os.path.join(self.base_dir, 'private/config')))
    # Check jio webdav folder
    self.assertTrue(os.path.exists(os.path.join(self.base_dir, 'private/config/.jio_documents')))
    self.assertTrue(os.path.exists(os.path.join(self.base_dir, 'private/documents')))

  def test_monitor_bootstrap_promises(self):
    self.configPromiseList(3)

    config_content = self.monitor_conf % self.monitor_config_dict
    self.writeContent(self.monitor_config_file, config_content)

    instance = Monitoring(self.monitor_config_file)
    instance.bootstrapMonitor()
    promise_file = os.path.join(self.base_dir, 'monitor-bootstrap-status')
    self.assertTrue(os.path.exists(promise_file))

    self.checkOPML([self.monitor_config_dict['base_url']])

    # Check update promises_list
    self.configPromiseList(5) # Add two promises
    os.unlink(os.path.join(self.base_dir, 'promise', 'monitor_promise-2')) # drop promise number 2
    instance2 = Monitoring(self.monitor_config_file)
    instance2.bootstrapMonitor()
    self.assertTrue(os.path.exists(promise_file))

  def test_monitor_bootstrap_genconfig(self):
    config_content = self.monitor_conf % self.monitor_config_dict
    self.writeContent(self.monitor_config_file, config_content)

    instance = Monitoring(self.monitor_config_file)
    instance.bootstrapMonitor()
    promise_file = os.path.join(self.base_dir, 'monitor-bootstrap-status')
    self.assertTrue(os.path.exists(promise_file))

    self.checkOPML([self.monitor_config_dict['base_url']])

    instance_config = os.path.join(instance.config_folder, '.jio_documents', 'config.json')
    self.assertTrue(os.path.exists(instance_config))
    config_content = json.loads(open(instance_config).read())
    self.assertEqual(len(config_content), 4)
    key_list = ['', 'sample', 'monitor-password', 'cors-domain']
    for parameter in config_content:
      if parameter['key'] in key_list:
        key_list.pop(key_list.index(parameter['key']))
      if parameter['key'] == '':
        self.assertEqual(parameter, dict(
          key="",
          title="monitor-user",
          value="admin"))
      if parameter['key'] == 'sample':
        self.assertEqual(parameter, dict(
          key="sample",
          title="sample",
          value="12345"))
      if parameter['key'] == 'monitor-password':
        self.assertEqual(parameter, dict(
          key="monitor-password",
          title="monitor-password",
          value="bcuandjy"))
      if parameter['key'] == 'cors-domain':
        self.assertEqual(parameter, dict(
          key="cors-domain",
          title="cors-domain",
          value=""))

    self.assertEqual(key_list, [])


