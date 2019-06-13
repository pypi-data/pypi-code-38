import mock
import os
import string
import random
import supervisor
import thread
import unittest


import slapos.runner.utils as runner_utils

import sys
sys.modules['slapos.runner.utils'].sup_process = mock.MagicMock()


class TestRunnerBackEnd(unittest.TestCase):
  def setUp(self):
    self.sup_process = runner_utils.sup_process
    self.sup_process.reset_mock()
    runner_utils.open = open

  def tearDown(self):
    garbage_file_list = [
      os.path.join(*(os.getcwd(), '.htpasswd')),
      os.path.join(*(os.getcwd(), '.turn-left')),
      os.path.join(*(os.getcwd(), 'slapos-test.cfg')),
    ]
    for garbage_file in garbage_file_list:
      if os.path.exists(garbage_file):
        os.remove(garbage_file)

  def _startSupervisord(self):
    cwd = os.getcwd()
    supervisord_config_file = os.path.join(cwd, 'supervisord.conf')
    open(supervisord_config_file, 'w').write("""
    """)
    supervisord = supervisor.supervisord.Supervisord('-c', supervisord_config_file)
    thread.start_new_thread()

  def test_UserCanLoginAndUpdateCredentials(self):
    """
    * Create a user with createNewUser
    * Tests user can login with checkUserCredential
    * Updates user password updateUserCredential
    * Checks user can login with new credentials
    """
    def generate_password():
      return "".join(random.sample( \
        string.ascii_letters + string.digits + string.punctuation, 20))

    config = {'etc_dir': os.getcwd()}
    login = "admin"
    password = generate_password()
    self.assertTrue(runner_utils.createNewUser(config, login, password))
    self.assertTrue(runner_utils.checkUserCredential(config, login, password))

    new_password = generate_password()
    self.assertNotEqual(password, new_password)
    runner_utils.updateUserCredential(config, login, new_password)
    self.assertTrue(runner_utils.checkUserCredential(config, login, new_password))

  @mock.patch('os.path.exists')
  def test_getCurrentSoftwareReleaseProfile(self, mock_path_exists):
    """
    * Mock a .project file
    * Tests that getCurrentSoftwareReleaseProfile returns an absolute path
    """
    cwd = os.getcwd()

    # If .project file doesn't exist, then getCurrentSoftwareReleaseProfile
    # returns an empty string
    config = {'etc_dir': os.path.join(cwd, 'etc'),
              'workspace': os.path.join(cwd, 'srv', 'runner'),
              'software_profile': 'software.cfg'}

    profile = runner_utils.getCurrentSoftwareReleaseProfile(config)
    self.assertEqual(profile, "")

    # If .project points to a SR that doesn't exist, returns empty string
    runner_utils.open = mock.mock_open(read_data="workspace/fake/path/")
    mock_path_exists.return_value = False
    profile = runner_utils.getCurrentSoftwareReleaseProfile(config)
    self.assertEqual(profile, "")

    # If software_profile exists, getCurrentSoftwareReleaseProfile should
    # return its absolute path
    runner_utils.open = mock.mock_open(read_data = "workspace/project/software/")
    mock_path_exists.return_value = True
    profile = runner_utils.getCurrentSoftwareReleaseProfile(config)
    self.assertEqual(profile, os.path.join(config['workspace'], 'project',
        'software', config['software_profile']))

  @mock.patch('os.mkdir')
  @mock.patch('slapos.runner.utils.updateProxy')
  @mock.patch('slapos.runner.utils.requestInstance')
  @mock.patch('slapos.runner.utils.config_SR_folder')
  def _runSlapgridWithLockMakesCorrectCallsToSupervisord(self,
                                                         run_slapgrid_function,
                                                         process_name,
                                                         mock_configSRFolder,
                                                         mock_requestInstance,
                                                         mock_updateProxy,
                                                         mock_mkdir):
    """
    Tests that runSoftwareWithLock and runInstanceWithLock make correct calls
    to sup_process (= supervisord)
    """
    mock_updateProxy.return_value = True
    cwd = os.getcwd()
    config = {'etc_dir': cwd,
              'software_root': os.path.join(cwd, 'software'),
              'software_log': os.path.join(cwd, 'software.log'),
              'instance_root': os.path.join(cwd, 'software'),
              'instance_log': os.path.join(cwd, 'software.log')}
    # If process is already running, then does nothing
    self.sup_process.isRunning.return_value = True
    self.assertEqual(run_slapgrid_function(config), 1)
    self.assertFalse(self.sup_process.runProcess.called)

    # If the slapgrid process is not running, it should start it
    self.sup_process.isRunning.return_value = False
    # First, without Lock
    run_slapgrid_function(config)
    self.sup_process.runProcess.assert_called_once_with(config, process_name)
    self.assertFalse(self.sup_process.waitForProcessEnd.called)
    # Second, with Lock
    self.sup_process.reset_mock()
    run_slapgrid_function(config, lock=True)
    self.sup_process.runProcess.assert_called_once_with(config, process_name)
    self.sup_process.waitForProcessEnd.assert_called_once_with(config, process_name)

  def test_runSoftwareWithLockMakesCorrectCallstoSupervisord(self):
    self._runSlapgridWithLockMakesCorrectCallsToSupervisord(
      runner_utils.runSoftwareWithLock, 'slapgrid-sr')

  def test_runInstanceWithLockMakesCorrectCallstoSupervisord(self):
    self._runSlapgridWithLockMakesCorrectCallsToSupervisord(
      runner_utils.runInstanceWithLock, 'slapgrid-cp')

  @mock.patch('os.path.exists')
  @mock.patch('os.remove')
  @mock.patch('slapos.runner.utils.startProxy')
  @mock.patch('slapos.runner.utils.stopProxy')
  @mock.patch('slapos.runner.utils.removeProxyDb')
  def test_changingSRUpdatesProjectFileWithExistingPath(self,
                                                        mock_removeProxyDb,
                                                        mock_stopProxy,
                                                        mock_startProxy,
                                                        mock_remove,
                                                        mock_path_exists):
    cwd = os.getcwd()
    config = {'etc_dir' : os.path.join(cwd, 'etc'),
              'workspace': os.path.join(cwd, 'srv', 'runner')}
    projectpath = 'workspace/project/software/'
    self.assertNotEqual(runner_utils.realpath(config, projectpath, \
                                              check_exist=False), '')

    # If projectpath doesn't exist, .project file shouldn't be written
    mock_path_exists.return_value = False
    result = runner_utils.configNewSR(config, projectpath)
    self.assertFalse(result)

    # If projectpath exist, .project file should be overwritten
    mock_path_exists.return_value = True
    runner_utils.open = mock.mock_open()
    result = runner_utils.configNewSR(config, projectpath)
    self.assertTrue(result)
    runner_utils.open.assert_has_calls([mock.call().write(projectpath)])

  @mock.patch('slapos.runner.utils.isInstanceRunning')
  @mock.patch('slapos.runner.utils.svcStopAll')
  def test_removingInstanceStopsProcessesAndCleansInstanceDirectory(self,
                                                                    mock_svcStopAll,
                                                                    mock_isInstanceRunning):
    """
    When removing the current running instances, processes should be stopped
    and directories deleted properly
    """
    cwd = os.getcwd()
    config = {'database_uri': os.path.join(cwd, 'proxy.db'),
              'etc_dir': os.path.join(cwd, 'etc'),
              'instance_root': os.path.join(cwd, 'instance'),}

    # If slapos node is running, removeCurrentInstance returns a string
    mock_isInstanceRunning.return_value = True
    self.assertTrue(isinstance(runner_utils.removeCurrentInstance(config), str))
    self.assertTrue(mock_isInstanceRunning.called)

    # If slapos is not running, process should be stopped and directories emptied
    mock_isInstanceRunning.return_value = False
    result = runner_utils.removeCurrentInstance(config)
    self.assertTrue(mock_svcStopAll.called)
    self.sup_process.stopProcess.assert_called_with(config, 'slapproxy')

  @mock.patch('os.listdir')
  @mock.patch('os.path.exists')
  @mock.patch('slapos.runner.utils.removeCurrentInstance')
  @mock.patch('slapos.runner.utils.removeSoftwareRootDirectory')
  def test_removingUsedSoftwareReleaseCleansInstancesToo(self,
                                                         mock_removeSoftwareRootDirectory,
                                                         mock_removeCurrentInstance,
                                                         mock_path_exists,
                                                         mock_listdir):
    """
    When removing the Software Release on which depends the current running
    instances, the current instances should be stopped and removed properly.
    """
    # mock_listir is needed for not raising in loadSoftwareRList or future equivalent
    mock_listdir.return_value = []

    cwd = os.getcwd()
    config = {'etc_dir': os.path.join(cwd, 'etc'),
              'software_root': os.path.join(cwd, 'software'),
              'software_link': os.path.join(cwd, 'softwareLink'),}

    self.sup_process.isRunning.return_value = False

    # First tests that if the current instance doesn't extend the Software
    # Release to delete, the instance isn't deleted
    runner_utils.open = mock.mock_open(read_data="/workspace/software/another/")
    runner_utils.removeSoftwareByName(config, '1234567890', 'my_software_name')

    self.assertFalse(mock_removeCurrentInstance.called)
    self.assertTrue(mock_removeSoftwareRootDirectory.called)

    # If the current Instance extends the Software Release, then both must
    # be removed
    mock_removeSoftwareRootDirectory.reset_mock()

    runner_utils.open = mock.mock_open(read_data="/workspace/software/my_software_name/")
    runner_utils.removeSoftwareByName(config, '1234567890', 'my_software_name')

    self.assertTrue(mock_removeCurrentInstance.called)
    self.assertTrue(mock_removeSoftwareRootDirectory.called)

  @mock.patch('slapos.runner.utils.runInstanceWithLock')
  @mock.patch('slapos.runner.utils.runSoftwareWithLock')
  def test_runSoftwareRunOnlyOnceIfSoftwareSuccessfullyCompiledOnFirstTime(self,
                                                                           mock_runSoftwareWithLock,
                                                                           mock_runInstanceWithLock):
    cwd = os.getcwd()
    config = {'runner_workdir': cwd,
              'etc_dir': cwd}

    build_and_run_parameter_dict = {
      'run_instance': False,
      'run_software': True,
      'max_run_instance': 3,
      'max_run_software': 3,
    }
    runner_utils.saveBuildAndRunParams(config, build_and_run_parameter_dict)

    # First, configuration is set to only run the compilation of the software release
    # Both runSoftwareWithLock and runInstanceWithLock succeed on 1st try
    mock_runSoftwareWithLock.return_value = 0
    mock_runInstanceWithLock.return_value = 0

    runner_utils.runSlapgridUntilSuccess(config, 'software')
    self.assertEqual(mock_runSoftwareWithLock.call_count, 1)
    self.assertEqual(mock_runInstanceWithLock.call_count, 0)

    # Second, instanciation should start if compilation succeeded
    mock_runSoftwareWithLock.reset_mock()
    build_and_run_parameter_dict.update({'run_instance': True})
    runner_utils.saveBuildAndRunParams(config, build_and_run_parameter_dict)

    runner_utils.runSlapgridUntilSuccess(config, 'software')
    self.assertEqual(mock_runSoftwareWithLock.call_count, 1)
    self.assertEqual(mock_runInstanceWithLock.call_count, 1)

  @mock.patch('slapos.runner.utils.runInstanceWithLock')
  @mock.patch('slapos.runner.utils.runSoftwareWithLock')
  def test_runSoftwareDonotRestartForeverEvenIfBuildoutFileIsWrong(self,
                                                                   mock_runSoftwareWithLock,
                                                                   mock_runInstanceWithLock):
    """
    Restarting compilation or instanciation should happen a limited number of
    times to prevent useless runs due to a mistaken buildout config.
    """
    cwd = os.getcwd()
    config = {'runner_workdir': cwd,
              'etc_dir': cwd}

    build_and_run_parameter_dict = {
      'run_instance': True,
      'run_software': True,
      'max_run_instance': 3,
      'max_run_software': 3,
    }
    runner_utils.saveBuildAndRunParams(config, build_and_run_parameter_dict)

    # runSoftwareWithLock always fail and runInstanceWithLock succeeds on 1st try
    mock_runSoftwareWithLock.return_value = 1
    mock_runInstanceWithLock.return_value = 0

    runner_utils.runSlapgridUntilSuccess(config, 'software')
    self.assertEqual(mock_runSoftwareWithLock.call_count,
                     build_and_run_parameter_dict['max_run_software'])
    # if running software fails, then no need to try to deploy instances
    self.assertEqual(mock_runInstanceWithLock.call_count, 0)

  @mock.patch('os.path.exists')
  @mock.patch('slapos.runner.utils.updateInstanceParameter')
  @mock.patch('slapos.runner.utils.isSoftwareReleaseCompleted')
  @mock.patch('slapos.runner.utils.runSlapgridUntilSuccess')
  @mock.patch('slapos.runner.utils.isSoftwareRunning')
  @mock.patch('slapos.runner.utils.runSoftwareWithLock')
  def test_isSoftwareReleaseReady(self,
                                  mock_runSoftwareWithLock,
                                  mock_isSoftwareRunning,
                                  mock_runSlapgridUntilSuccess,
                                  mock_isSoftwareReleaseCompleted,
                                  mock_updateInstanceParameter,
                                  mock_path_exists):
    cwd = os.getcwd()
    config = {
      'etc_dir': cwd,
      'runner_workdir': cwd,
      'slapos-software': 'slapos/dummy',
      'auto_deploy': False,
      'autorun': False,
    }
    # Every parameter is False, so do nothing
    self.assertEqual(runner_utils.isSoftwareReleaseReady(config), '0')

    # We define a software, so from now we expect to build
    mock_path_exists.return_value = True

    # auto_deploy is True, so Software Release should build
    config.update({
      'auto_deploy': True,
    })

    # slapgrid-sr is running
    mock_isSoftwareRunning.return_value = True
    mock_isSoftwareReleaseCompleted.return_value = False
    self.assertEqual(runner_utils.isSoftwareReleaseReady(config), '2')
    
    # SR is not built, and slapgrid-sr is not running, so it should be started
    mock_isSoftwareRunning.return_value = False
    mock_isSoftwareReleaseCompleted.return_value = False

    self.assertEqual(runner_utils.isSoftwareReleaseReady(config), '2')
    self.assertTrue(mock_runSoftwareWithLock.called)

    mock_runSoftwareWithLock.reset_mock()

    # SR is built
    mock_isSoftwareReleaseCompleted.return_value = True
    self.assertEqual(runner_utils.isSoftwareReleaseReady(config), '1')

    # If autorun is True, Instance is expected to build too
    config.update({
      'autorun': True,
    })
    mock_isSoftwareRunning.return_value = False
    mock_isSoftwareReleaseCompleted.return_value = True

    self.assertEqual(runner_utils.isSoftwareReleaseReady(config), '1')
    mock_runSlapgridUntilSuccess.assert_called_with(config, 'instance')


  @unittest.skip('No scenario defined')
  def test_autoDeployWontEraseExistingInstances(self):
    raise NotImplementedError

  @unittest.skip('No scenario defined')
  def test_requestingInstanceCorrectlyPassesTypeAndParameters(self):
    raise NotImplementedError

  @unittest.skip('No scenario defined')
  def test_parametersAreCorrectlyUpdatedAndGivenToTheInstance(self):
    raise NotImplementedError


if __name__ == '__main__':
  random.seed()
  unittest.main()
