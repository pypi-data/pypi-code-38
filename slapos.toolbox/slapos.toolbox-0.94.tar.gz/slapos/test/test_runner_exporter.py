import mock
import os
import shutil
import time
import unittest

from slapos.resilient import runner_exporter
from StringIO import StringIO

tested_instance_cfg = """[buildout]
installed_develop_eggs = 
parts = folders hello-nicolas hello-rafael exclude

[folders]
__buildout_installed__ = 
__buildout_signature__ = wcwidth-0.1.7-py2.7.egg contextlib2-0.5.5-py2.7.egg ...
etc = /some/prefix/slappart18/test/etc
home = /srv/slapgrid/slappart18/test
recipe = slapos.cookbook:mkdirectory
srv = /some/prefix/slappart18/test/srv

[hello-nicolas]
__buildout_installed__ = {cwd}/instance/slappart0/etc/nicolas.txt
__buildout_signature__ = MarkupSafe-1.0-py2.7-linux-x86_64.egg Jinja2-2.10-py2.7.egg zc.buildout-2.12.2-py2.7.egg slapos.recipe.template-4.3-py2.7.egg setuptools-40.4.3-py2.7.egg
mode = 0644
name = Nicolas
output = /some/prefix/slappart18/test/etc/nicolas.txt
recipe = slapos.recipe.template

[hello-rafael]
__buildout_installed__ = {cwd}/instance/slappart0/etc//rafael.txt
__buildout_signature__ = MarkupSafe-1.0-py2.7-linux-x86_64.egg Jinja2-2.10-py2.7.egg zc.buildout-2.12.2-py2.7.egg slapos.recipe.template-4.3-py2.7.egg setuptools-40.4.3-py2.7.egg
name = Rafael
output = /some/prefix/slappart18/test/etc/rafael.txt
recipe = slapos.recipe.template

[exclude]
__buildout_installed__ = {cwd}/instance/slappart0/srv/exporter.exclude
__buildout_signature__ = MarkupSafe-1.0-py2.7-linux-x86_64.egg Jinja2-2.10-py2.7.egg zc.buildout-2.12.2-py2.7.egg slapos.recipe.template-4.3-py2.7.egg setuptools-40.4.3-py2.7.egg
recipe = slapos.recipe.template:jinja2
rendered = /some/prefix/slappart18/test/srv/exporter.exclude
template = inline:
        srv/backup/*.log

[exclude1]
__buildout_installed__ = {cwd}/instance/slappart1/srv/exporter.exclude
__buildout_signature__ = MarkupSafe-1.0-py2.7-linux-x86_64.egg Jinja2-2.10-py2.7.egg zc.buildout-2.12.2-py2.7.egg slapos.recipe.template-4.3-py2.7.egg setuptools-40.4.3-py2.7.egg
recipe = slapos.recipe.template:jinja2
rendered = /some/prefix/slappart18/test/srv/exporter.exclude
template = inline:
        srv/backup/log/**"""


class Config():
  pass


class TestRunnerExporter(unittest.TestCase):
  def setUp(self):
    if not os.path.exists('test_folder'):
      os.mkdir('test_folder')
      os.chdir('test_folder')


  def tearDown(self):
    if os.path.basename(os.getcwd()) == 'test_folder':
      os.chdir('..')
      shutil.rmtree('test_folder')
    elif 'test_folder' in os.listdir('.'):
      shutil.rmtree('test_folder')

  def _createFile(self, path, content=''):
    with open(path, 'w') as f:
      f.write(content)

  def _createExecutableFile(self, path, content=''):
    self._createFile(path, content)
    os.chmod(path, 0700)

  def _setUpFakeInstanceFolder(self):
    self._createFile('proxy.db')
    os.makedirs('project')
    os.makedirs('public')

    """Create data mirroring tested_instance_cfg"""
    os.makedirs('instance/slappart0/etc')
    os.makedirs('instance/slappart0/srv/backup/important_logs')

    os.makedirs('instance/slappart1/etc')
    os.makedirs('instance/slappart1/srv/backup/log')

    self._createFile('instance/slappart0/.installed.cfg',
                     tested_instance_cfg.format(cwd=os.getcwd()))

    self._createFile('instance/slappart0/srv/backup/data.dat',
                     'all my fortune lays on this secret !')
    self._createFile('instance/slappart0/srv/backup/important_logs/this_is_a.log',
                     'this log is very important !')
    self._createFile('instance/slappart0/srv/backup/data.log',
                     'this log is not so important !')
    self._createFile('instance/slappart0/srv/exporter.exclude',
                     'srv/backup/*.log')

    self._createFile('instance/slappart0/etc/config.json')
    self._createFile('instance/slappart0/etc/.parameters.xml')
    self._createFile('instance/slappart0/etc/.project',
                     'workspace/slapos-dev/software/erp5')

    self._createFile('instance/slappart1/srv/backup/data.dat',
                     'This is important data also !')
    self._createFile('instance/slappart1/srv/backup/log/log1',
                     'First log')
    self._createFile('instance/slappart1/srv/backup/log/log2',
                     'Second log')
    self._createFile('instance/slappart1/srv/exporter.exclude',
                     'srv/backup/log/**')

    self._createExecutableFile(
      'instance/slappart1/srv/.backup_identity_script',
      "#!/bin/sh\nexec xargs -0 md5sum"
    )


  def test_CwdContextManager(self):
    os.makedirs('a/b')
    with runner_exporter.CwdContextManager('a'):
      self.assertEqual(os.listdir('.'), ['b'])
      os.mkdir('c')
    self.assertEqual(os.listdir('.'), ['a'])
    self.assertEqual(sorted(os.listdir('a')), ['b', 'c'])


  def test_getExcludePathList(self):
    self._setUpFakeInstanceFolder()
    self.assertEqual(
      sorted(runner_exporter.getExcludePathList(os.getcwd())),
      [
        '*.pid',
        '*.sock',
        '*.socket',
        '.installed*.cfg',
        'instance/slappart0/etc/nicolas.txt',
        'instance/slappart0/etc/rafael.txt',
        'instance/slappart0/srv/backup/*.log',
        'instance/slappart0/srv/exporter.exclude',
        'instance/slappart1/srv/backup/log/**',
        'instance/slappart1/srv/exporter.exclude',
      ]
    )


  @mock.patch('subprocess.check_output')
  def test_synchroniseRunnerConfigurationDirectory(self, check_output_mock):
    self._setUpFakeInstanceFolder()
    config = Config()
    config.rsync_binary = 'rsync'
    config.dry = False
    with runner_exporter.CwdContextManager('instance/slappart0/etc'):
      runner_exporter.synchroniseRunnerConfigurationDirectory(
        config, 'backup/runner/etc/'
      )
    self.assertEqual(check_output_mock.call_count, 1)
    check_output_mock.assert_any_call(
      ['rsync', '-rlptgov', '--stats', '--safe-links', '--ignore-missing-args', '--delete', '--delete-excluded', '.parameters.xml', '.project', 'config.json', 'backup/runner/etc/']
    )


  @mock.patch('subprocess.check_output')
  def test_synchroniseRunnerWorkingDirectory(self, check_output_mock):
    self._setUpFakeInstanceFolder()
    config = Config()
    config.rsync_binary = 'rsync'
    config.dry = False
    with runner_exporter.CwdContextManager(os.getcwd()):
      runner_exporter.synchroniseRunnerWorkingDirectory(
        config, 'backup/runner/runner'
      )

    self.assertEqual(check_output_mock.call_count, 1)
    check_output_mock.assert_any_call(
      ['rsync', '-rlptgov', '--stats', '--safe-links', '--ignore-missing-args', '--delete', '--delete-excluded', '--exclude=*.pid', '--exclude=*.sock', '--exclude=*.socket', '--exclude=.installed*.cfg', '--exclude=instance/slappart0/etc/nicolas.txt', '--exclude=instance/slappart0/etc/rafael.txt', '--exclude=instance/slappart0/srv/backup/*.log', '--exclude=instance/slappart0/srv/exporter.exclude', '--exclude=instance/slappart1/srv/backup/log/**', '--exclude=instance/slappart1/srv/exporter.exclude', 'instance', 'project', 'proxy.db', 'public', 'backup/runner/runner']
    )

  def test_getSlappartSignatureMethodDict(self):
    self._setUpFakeInstanceFolder()
    slappart_signature_method_dict = runner_exporter.getSlappartSignatureMethodDict()
    self.assertEqual(
      slappart_signature_method_dict,
      {
        './instance/slappart1': './instance/slappart1/srv/.backup_identity_script',
      }
    )
    

  def test_writeSignatureFile(self):
    self._setUpFakeInstanceFolder()

    os.makedirs('backup/etc')
    os.makedirs('backup/runner/instance/slappart0')
    os.makedirs('backup/runner/instance/slappart1')

    self._createFile('backup/etc/.project', 'workspace/slapos-dev/software/erp5')
    self._createFile('backup/runner/instance/slappart0/data', 'hello')
    self._createFile('backup/runner/instance/slappart1/data', 'world')

    os.symlink('data', 'backup/runner/instance/slappart0/good_link')
    os.symlink(os.path.abspath('backup/runner/instance/slappart0/data'), 'backup/runner/instance/slappart0/good_abs_link')
    os.symlink('unexisting_file', 'backup/runner/instance/slappart0/bad_link')

    slappart_signature_method_dict = {
      './instance/slappart1': './instance/slappart1/srv/.backup_identity_script',
    }

    with runner_exporter.CwdContextManager('backup'):
      runner_exporter.writeSignatureFile(slappart_signature_method_dict, '..', signature_file_path='backup.signature')

      with open('backup.signature', 'r') as f:
        signature_file_content = f.read()

    # Slappart1 is using md5sum as signature, others are using sha256sum (default)
    self.assertEqual(signature_file_content,
       """2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824  ./runner/instance/slappart0/data
2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824  ./runner/instance/slappart0/good_abs_link
2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824  ./runner/instance/slappart0/good_link
49b74873d57ff0307b7c9364e2fe2a3876d8722fbe7ce3a6f1438d47647a86f4  ./etc/.project
7d793037a0760186574b0282f2f435e7  ./runner/instance/slappart1/data""")

  def test_getBackupFilesModifiedDuringExportList(self):
    self._setUpFakeInstanceFolder()
    config = Config()
    config.rsync_binary = 'rsync'

    self.assertEqual(
      runner_exporter.getBackupFilesModifiedDuringExportList(config, time.time() - 5),
      ['instance/slappart0/srv/backup/data.dat',
       'instance/slappart0/srv/backup/important_logs/this_is_a.log',
       'instance/slappart1/srv/backup/data.dat']
    )
    time.sleep(2)
    self.assertFalse(
      runner_exporter.getBackupFilesModifiedDuringExportList(config, time.time() - 1)
    )
    self._createFile('instance/slappart1/srv/backup/bakckup.data', 'my backup')
    self.assertEqual(
      runner_exporter.getBackupFilesModifiedDuringExportList(config, time.time() - 1),
      ['instance/slappart1/srv/backup/bakckup.data']
    )
