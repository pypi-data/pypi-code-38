# -*- coding: utf-8 -*-
# vim: set et sts=2:
# pylint: disable-msg=W0311,C0301,C0103,C0111,R0904

#############################################
# !!! Attention !!!
# You now have to comment the last line
# in __init__py, wich starts the functiun
# run() in order to start the tests,
# or it will NOT work
#############################################

import argparse
import base64
import ConfigParser
import datetime
import hashlib
import json
import os
import shutil
import sup_process
from StringIO import StringIO
import ssl
import time
import unittest
import urllib2

from slapos.runner.utils import (getProfilePath,
                                 getSession, isInstanceRunning,
                                 isSoftwareRunning, startProxy,
                                 isSoftwareReleaseReady,
                                 runSlapgridUntilSuccess, runInstanceWithLock,
                                 getBuildAndRunParams, saveBuildAndRunParams)
from slapos.runner import views
import slapos.slap
from slapos.htpasswd import  HtpasswdFile
from .run import Config

import erp5.util.taskdistribution as taskdistribution


#Helpers
def loadJson(response):
  return json.loads(response.data)

def parseArguments():
  """
  Parse arguments for erp5testnode-backed test.
  """
  parser = argparse.ArgumentParser()

  # runnertest mandatory arguments
  parser.add_argument('--key_file',
                      metavar='KEY_FILE',
                      help='Path to the key file used to communicate with slapOS-master')

  parser.add_argument('--cert_file',
                      metavar='CERT_FILE',
                      help='Path to the cert file used to communicate with slapOS-master')

  parser.add_argument('--server_url',
                      metavar='SERVER_URL',
                      help='URL of the local slapproxy')

  parser.add_argument('--computer_id',
                      metavar='COMPUTER_ID',
                      help='ID of the COMP where the slaprunner is running')

  parser.add_argument('--partition_id',
                      metavar='PARTITION_ID',
                      help='ID of the partition where the slaprunner is depoyed')

  # Test Node arguments
  parser.add_argument('--test_result_path',
                      metavar='ERP5_TEST_RESULT_PATH',
                      help='ERP5 relative path of the test result')

  parser.add_argument('--revision',
                      metavar='REVISION',
                      help='Revision of the test_suite')

  parser.add_argument('--test_suite',
                      metavar='TEST_SUITE',
                      help='Name of the test suite')

  parser.add_argument('--test_suite_title',
                      metavar='TEST_SUITE',
                      help='The test suite title')

  parser.add_argument('--test_node_title',
                      metavar='NODE_TITLE',
                      help='Title of the testnode which is running this'
                            'launcher')

  parser.add_argument('--project_title',
                      metavar='PROJECT_TITLE',
                      help='The project title')

  parser.add_argument('--node_quantity', help='Number of parallel tests to run',
                      default=1, type=int)

  parser.add_argument('--master_url',
                      metavar='TEST_SUITE_MASTER_URL',
                      help='Url to connect to the ERP5 Master testsuite taskditributor')

  return parser.parse_args()


class SlaprunnerTestCase(unittest.TestCase):

  @classmethod
  def setUpClass(cls, **kw):
    if len(kw) == 0:
      return
    cls.server_url = kw['server_url']
    cls.key_file = kw['key_file']
    cls.cert_file = kw['cert_file']
    cls.computer_id = kw['computer_id']
    cls.partition_id = kw['partition_id']
    # Get parameters returned by slapos master
    slap = slapos.slap.slap()
    slap.initializeConnection(cls.server_url, cls.key_file, cls.cert_file)
    cls.partition = slap.registerComputerPartition(
      computer_guid=cls.computer_id,
      partition_id=cls.partition_id
    )
    cls.parameter_dict = cls.partition.getConnectionParameterDict()
    for attribute, value in cls.parameter_dict.iteritems():
      setattr(cls, attribute.replace('-', '_'), value)

    #create slaprunner configuration
    views.app.config['TESTING'] = True
    config = Config()
    config.setConfig()
    views.app.config.update(**config.__dict__)
    cls.app = views.app.test_client()
    cls.app.config = views.app.config

    # Set up path (needed to find git binary)
    os.environ['PATH'] = config.path

  def setUp(self):
    """Initialize slapos webrunner here"""
    self.users = [self.init_user, self.init_password, "slaprunner@nexedi.com", "SlapOS web runner"]
    self.updateUser = ["newslapuser", "newslappwd", "slaprunner@nexedi.com", "SlapOS web runner"]
    self.repo = 'https://lab.nexedi.com/rafael/slapos-workarround.git'
    self.software = "workspace/slapos/software/"  # relative directory fo SR
    self.project = 'slapos'  # Default project name
    self.template = 'template.cfg'
    self.partitionPrefix = 'slappart'

    self.workdir = workdir = os.path.join(self.app.config['runner_workdir'], 'project')
    software_link = os.path.join(self.app.config['runner_workdir'], 'softwareLink')
    #update or create all runner base directory to test_dir
    if not os.path.exists(workdir):
      os.mkdir(workdir)
    if not os.path.exists(software_link):
      os.mkdir(software_link)

    #Create config.json
    json_file = os.path.join(views.app.config['etc_dir'], 'config.json')
    if not os.path.exists(json_file):
      params = {
        'run_instance' : True,
        'run_software' : True,
        'max_run_instance' : 3,
        'max_run_software' : 2
      }
      open(json_file, "w").write(json.dumps(params))

  def tearDown(self):
    """Remove all test data"""
    project = os.path.join(self.app.config['etc_dir'], '.project')

    #reset tested parameters
    self.updateConfigParameter('autorun', False)
    self.updateConfigParameter('auto_deploy', True)

    if os.path.exists(project):
      os.unlink(project)
    if os.path.exists(self.app.config['workspace']):
      shutil.rmtree(self.app.config['workspace'])
    if os.path.exists(self.app.config['software_root']):
      shutil.rmtree(self.app.config['software_root'])
    if os.path.exists(self.app.config['instance_root']):
      shutil.rmtree(self.app.config['instance_root'])
    if os.path.exists(self.app.config['software_link']):
      shutil.rmtree(self.app.config['software_link'])

  def updateConfigParameter(self, parameter, value):
    config_parser = ConfigParser.SafeConfigParser()
    config_parser.read(os.getenv('RUNNER_CONFIG'))
    for section in config_parser.sections():
      if config_parser.has_option(section, parameter):
        config_parser.set(section, parameter, str(value))
    with open(os.getenv('RUNNER_CONFIG'), 'wb') as configfile:
      config_parser.write(configfile)


  def updateAccount(self, newaccount):
    """Helper for update user account data"""
    return self.app.post('/updateAccount',
                         data=dict(
                           username=newaccount[0],
                           password=newaccount[1],
                           email=newaccount[2],
                           name=newaccount[3],
                         ),
                         follow_redirects=True)

  def getCurrentSR(self):
   return getProfilePath(self.app.config['etc_dir'],
                              self.app.config['software_profile'])

  def setupProjectFolder(self):
    """Helper to create a project folder as for slapos.git"""
    base = os.path.join(self.app.config['workspace'], 'slapos')
    software = os.path.join(base, 'software')
    os.mkdir(base)
    os.mkdir(software)

  def setupTestSoftware(self):
    """Helper to setup Basic SR for testing purposes"""
    self.setupProjectFolder()
    base = os.path.join(self.app.config['workspace'], 'slapos')
    software = os.path.join(base, 'software')
    testSoftware = os.path.join(software, 'slaprunner-test')
    sr = "[buildout]\n\n"
    sr += "parts = command\n\nunzip = true\nnetworkcache-section = networkcache\n\n"
    sr += "find-links += http://www.nexedi.org/static/packages/source/slapos.buildout/\n\n"
    sr += "[networkcache]\ndownload-cache-url = http://www.shacache.org/shacache"
    sr += "\ndownload-dir-url = http://www.shacache.org/shadir\n\n"
    sr += "[command]\nrecipe = zc.recipe.egg\neggs = plone.recipe.command\n  zc.buildout\n\n"
    sr += """
[versions]
setuptools = 33.1.1
"""
    os.mkdir(testSoftware)
    open(os.path.join(testSoftware, self.app.config['software_profile']),
         'w').write(sr)
    md5 = hashlib.md5(os.path.join(self.app.config['workspace'],
                                   "slapos/software/slaprunner-test",
                                   self.app.config['software_profile'])
                      ).hexdigest()
    base = os.path.join(self.app.config['software_root'], md5)
    template = os.path.join(base, self.template)
    content = "[buildout]\n"
    content += "parts = \n  create-file\n\n"
    content += "eggs-directory = %s\n" % os.path.join(base, 'eggs')
    content += "develop-eggs-directory = %s\n\n" % os.path.join(base, 'develop-eggs')
    content += "[create-file]\nrecipe = plone.recipe.command\n"
    content += "filename = ${buildout:directory}/etc\n"
    content += "command = mkdir ${:filename} && echo 'simple file' > ${:filename}/testfile\n"
    os.mkdir(self.app.config['software_root'])
    os.mkdir(base)
    open(template, "w").write(content)

  def assertCanLoginWith(self, username, password):
    request = urllib2.Request(self.backend_url)
    base64string = base64.encodestring('%s:%s' % (username, password))[:-1]
    request.add_header("Authorization", "Basic %s" % base64string)
    ssl_context = ssl._create_unverified_context()
    result = urllib2.urlopen(request, context=ssl_context)
    self.assertEqual(result.getcode(), 200)

  def test_updateAccount(self):
    """test Update accound, this needs the user to log in"""
    # Check that given user can log in
    self.assertCanLoginWith(self.users[0], self.users[1])
    # Adds a user
    new_user = {'username': 'vice-president', 'password': '123456'}
    response = loadJson(self.app.post('/addUser', data=new_user))
    self.assertEqual(response['code'], 1)
    self.assertCanLoginWith(new_user['username'], new_user['password'])


  def test_cloneProject(self):
    """Start scenario 1 for deploying SR: Clone a project from git repository"""
    folder = 'workspace/' + self.project
    if os.path.exists(self.app.config['workspace'] + '/' + self.project):
      shutil.rmtree(self.app.config['workspace'] + '/' + self.project)
    data = {
      'repo': self.repo,
      'user': 'Slaprunner test',
      'email': 'slaprunner@nexedi.com',
      'name': folder
    }
    response = loadJson(self.app.post('/cloneRepository', data=data,
                    follow_redirects=True))
    self.assertEqual(response['result'], "")
    # Get realpath of create project
    path_data = dict(file=folder)
    response = loadJson(self.app.post('/getPath', data=path_data,
                    follow_redirects=True))
    self.assertEqual(response['code'], 1)
    realFolder = response['result'].split('#')[0]
    #Check git configuration
    config = open(os.path.join(realFolder, '.git/config')).read()
    assert "slaprunner@nexedi.com" in config and "Slaprunner test" in config

    # Checkout to slaprunner branch, this supposes that branch slaprunner exit
    response = loadJson(self.app.post('/newBranch',
                                      data=dict(
                                        project=folder,
                                        create='0',
                                        name='erp5'
                                      ),
                                      follow_redirects=True))
    self.assertEqual(response['result'], "")

  def test_createSR(self):
    """Scenario 2: Create a new software release"""
    #setup project directory
    self.setupProjectFolder()
    newSoftware = os.path.join(self.software, 'slaprunner-test')
    response = loadJson(self.app.post('/createSoftware',
                                      data=dict(folder=newSoftware),
                                      follow_redirects=True))
    self.assertEqual(response['result'], "")
    currentSR = self.getCurrentSR()
    assert newSoftware in currentSR

  def test_openSR(self):
    """Scenario 3: Open software release"""
    self.test_cloneProject()
    software = os.path.join(self.software, 'helloworld')  # Drupal SR must exist in SR folder
    response = loadJson(self.app.post('/setCurrentProject',
                                      data=dict(path=software),
                                      follow_redirects=True))
    self.assertEqual(response['result'], "")
    currentSR = self.getCurrentSR()
    assert software in currentSR
    self.assertFalse(isInstanceRunning(self.app.config))
    self.assertFalse(isSoftwareRunning(self.app.config))


  def test_runSoftware(self):
    """Scenario 4: CReate empty SR and save software.cfg file
      then run slapgrid-sr
    """
    #Call config account
    #call create software Release
    self.test_createSR()
    newSoftware = self.getCurrentSR()
    softwareRelease = "[buildout]\n\nparts =\n  test-application\n"
    softwareRelease += "#Test download git web repos éè@: utf-8 caracters\n"
    softwareRelease += "[test-application]\nrecipe = hexagonit.recipe.download\n"
    softwareRelease += "url = https://lab.nexedi.com/rafael/slapos-workarround.git\n" 
    softwareRelease += "filename = slapos.git\n"
    softwareRelease += "download-only = true\n"
    softwareRelease += "[versions]\nsetuptools = 33.1.1"
    response = loadJson(self.app.post('/saveFileContent',
                                      data=dict(file=newSoftware,
                                                content=softwareRelease),
                                      follow_redirects=True))
    self.assertEqual(response['result'], "")

    # Compile software and wait until slapgrid ends
    # this is supposed to use current SR
    while self.app.get('/isSRReady').data == "2":
      time.sleep(2)
    self.assertEqual(self.app.get('/isSRReady').data, "1")
    self.assertTrue(os.path.exists(self.app.config['software_root']))
    self.assertTrue(os.path.exists(self.app.config['software_log']))
    assert "test-application" in open(self.app.config['software_log']).read()
    sr_dir = os.listdir(self.app.config['software_root'])
    self.assertEqual(len(sr_dir), 1)
    createdFile = os.path.join(self.app.config['software_root'], sr_dir[0],
                              'parts', 'test-application', 'slapos.git')
    self.assertTrue(os.path.exists(createdFile))


  def test_updateInstanceParameter(self):
    """Scenario 5: Update parameters of current sofware profile"""
    self.setupTestSoftware()
    #Set current projet and run Slapgrid-cp
    software = self.software + 'slaprunner-test/'
    response = loadJson(self.app.post('/setCurrentProject',
                                      data=dict(path=software),
                                      follow_redirects=True))
    self.assertEqual(response['result'], "")
    #Send paramters for the instance
    parameterDict = dict(appname='slaprunnerTest', cacountry='France')
    parameterXml = '<?xml version="1.0" encoding="utf-8"?>\n<instance>'
    parameterXml += '<parameter id="appname">slaprunnerTest</parameter>\n'
    parameterXml += '<parameter id="cacountry">France</parameter>\n</instance>'
    software_type = 'production'
    response = loadJson(self.app.post('/saveParameterXml',
                                      data=dict(parameter=parameterXml,
                                                software_type=software_type),
                                      follow_redirects=True))
    self.assertEqual(response['result'], "")
    slap = slapos.slap.slap()
    slap.initializeConnection(self.app.config['master_url'])
    computer = slap.registerComputer(self.app.config['computer_id'])
    partitionList = computer.getComputerPartitionList()
    self.assertNotEqual(partitionList, [])
    #Assume that the requested partition is partition 0
    slapParameterDict = partitionList[0].getInstanceParameterDict()
    self.assertTrue('appname' in slapParameterDict)
    self.assertTrue('cacountry' in slapParameterDict)
    self.assertEqual(slapParameterDict['appname'], 'slaprunnerTest')
    self.assertEqual(slapParameterDict['cacountry'], 'France')
    self.assertEqual(slapParameterDict['slap_software_type'], 'production')

    #test getParameterXml for webrunner UI
    response = loadJson(self.app.get('/getParameterXml/xml'))
    self.assertEqual(parameterXml, response['result'])
    response = loadJson(self.app.get('/getParameterXml/dict'))
    self.assertEqual(parameterDict, response['result']['instance'])


  def test_requestInstance(self):
    """Scenario 6: request software instance"""
    self.test_updateInstanceParameter()
    #run Software profile
    response = loadJson(self.app.post('/runSoftwareProfile',
                                      data=dict(),
                                      follow_redirects=True))
    while self.app.get('/isSRReady').data == "2":
      time.sleep(2)
    self.assertEqual(self.app.get('/isSRReady').data, "1")
    #run instance profile
    response = loadJson(self.app.post('/runInstanceProfile',
                                      data=dict(),
                                      follow_redirects=True))
    self.assertTrue(response['result'])
    # lets some time to the Instance to be deployed
    time.sleep(5)
    #Check that all partitions has been created
    assert "create-file" in open(self.app.config['instance_log']).read()
    for num in range(int(self.app.config['partition_amount'])):
      partition = os.path.join(self.app.config['instance_root'],
                    self.partitionPrefix + str(num))
      self.assertTrue(os.path.exists(partition))

    #Go to partition 0
    instancePath = os.path.join(self.app.config['instance_root'],
                         self.partitionPrefix + '0')
    createdFile = os.path.join(instancePath, 'etc', 'testfile')
    self.assertTrue(os.path.exists(createdFile))
    assert 'simple file' in open(createdFile).read()


  def test_safeAutoDeploy(self):
    """Scenario 7: isSRReady won't overwrite the existing
    Sofware Instance if it has been deployed yet"""
    # Test that SR won't be deployed with auto_deploy=False
    self.updateConfigParameter('auto_deploy', False)
    self.updateConfigParameter('autorun', False)
    project = open(os.path.join(self.app.config['etc_dir'],
                  '.project'), "w")
    project.write(self.software + 'slaprunner-test/')
    project.close()
    response = isSoftwareReleaseReady(self.app.config)
    self.assertEqual(response, "0")
    # Test if auto_deploy parameter starts the deployment of SR
    self.updateConfigParameter('auto_deploy', True)
    self.setupTestSoftware()
    response = isSoftwareReleaseReady(self.app.config)
    self.assertEqual(response, "2")
    # Test that the new call to isSoftwareReleaseReady
    # doesn't overwrite the previous installed one
    sup_process.killRunningProcess(self.app.config, 'slapgrid-sr')
    completed_path = os.path.join(self.app.config['runner_workdir'],
        'softwareLink', 'slaprunner-test', '.completed')
    completed_text = ".completed file: test"
    completed = open(completed_path, "w")
    completed.write(completed_text)
    completed.close()
    response = isSoftwareReleaseReady(self.app.config)
    self.assertEqual(response, "1")
    assert completed_text in open(completed_path).read()

  def test_maximumRunOfSlapgrid(self):
    """Scenario 8: runSlapgridUntilSucces run until a defined maximum of time
    slapgrid-sr and slapgrid-cp if it fails. It can also run only one or both
    of them if it is defined so
    We directly calls runSlapgridUntilSuccess, because we want
    to test the return code of the function"""
    # Installs a wrong buildout which will fail
    MAX_RUN_SOFTWARE = getBuildAndRunParams(self.app.config)['max_run_software']
    MAX_RUN_INSTANCE = getBuildAndRunParams(self.app.config)['max_run_instance']
    self.test_createSR()
    newSoftware = self.getCurrentSR()
    softwareRelease = "[buildout]\n\nparts =\n  test-application\n"
    softwareRelease += "find-links += http://www.nexedi.org/static/packages/source/slapos.buildout/\n\n"
    softwareRelease += "[networkcache]\ndownload-cache-url = http://www.shacache.org/shacache"
    softwareRelease += "\ndownload-dir-url = http://www.shacache.org/shadir\n\n"
    softwareRelease += "#Test download git web repos éè@: utf-8 caracters\n"
    softwareRelease += "[test-application]\nrecipe = slapos.cookbook:mkdirectory\n"
    softwareRelease += "test = /root/test\n"
    softwareRelease += """
[versions]
setuptools = 33.1.1
"""
    response = loadJson(self.app.post('/saveFileContent',
                                      data=dict(file=newSoftware,
                                                content=softwareRelease),
                                      follow_redirects=True))
    response = runSlapgridUntilSuccess(self.app.config, 'software')
    self.assertEqual(response, MAX_RUN_SOFTWARE)
    # clean folders for other tests
    workdir = os.path.join(self.app.config['runner_workdir'], 'project')
    git_repo = os.path.join(workdir, 'slapos')
    if os.path.exists(git_repo):
      shutil.rmtree(git_repo)
    # Installs a software which deploys, but fails while instanciating
    # preparation
    base = os.path.join(self.app.config['workspace'], 'slapos')
    software = os.path.join(base, 'software')
    testSoftware = os.path.join(software, 'slaprunner-test')
    if not os.path.exists(testSoftware):
      os.makedirs(testSoftware)
    software_cfg = os.path.join(testSoftware, 'software.cfg')
    instance_cfg = os.path.join(testSoftware, 'instance.cfg')
    # software.cfg
    softwareRelease = "[buildout]\n\nparts =\n  failing-template\n\n"
    softwareRelease += "[failing-template]\nrecipe = hexagonit.recipe.download\n"
    softwareRelease += "url = %s\n" % (instance_cfg)
    softwareRelease += "destination = ${buildout:directory}\n"
    softwareRelease += "download-only = true\n"
    open(software_cfg, 'w+').write(softwareRelease)
    # instance.cfg
    content = "[buildout]\n\nparts =\n fail\n"
    content += "[fail]\nrecipe=plone.recipe.command\n"
    content += "command = exit 1"
    open(instance_cfg, 'w+').write(content)
    project = open(os.path.join(self.app.config['etc_dir'],
                  '.project'), "w")
    project.write(self.software + 'slaprunner-test')
    project.close()
    # Build and Run
    parameters = getBuildAndRunParams(self.app.config)
    parameters['run_instance'] = False
    saveBuildAndRunParams(self.app.config, parameters)
    response = runSlapgridUntilSuccess(self.app.config, 'software')
    self.assertEqual(response, 1)
    parameters['run_instance'] = True
    saveBuildAndRunParams(self.app.config, parameters)
    response = runSlapgridUntilSuccess(self.app.config, 'software')
    self.assertEqual(response, (1, MAX_RUN_INSTANCE))

  def test_slaveInstanceDeployment(self):
    """
    In order to test both slapproxy and core features of
    slaprunner, will install special Software Release
    into the current webrunner and fetch its instance
    parameters once deployed.
    """
    # XXX: This test should NOT be a unit test but should be run
    # by a Test Agent running against a slapproxy.

    # Deploy "test-slave-instance-deployment" Software Release
    self.test_cloneProject()
    software = os.path.join(self.software, 'test-slave-instance-deployment')

    # Checkout to master branch
    response = loadJson(self.app.post('/newBranch',
                                      data=dict(
                                        project=self.workdir+'/slapos',
                                        create='0',
                                        name='master'
                                      ),
                                      follow_redirects=True)).get(u'code')
    self.assertEqual(response, 1)
    response = loadJson(self.app.post('/setCurrentProject',
                                      data=dict(path=software),
                                      follow_redirects=True)).get(u'code')
    self.assertEqual(response, 1)

    response = loadJson(self.app.post('/saveParameterXml',
                                      data=dict(parameter='<?xml version="1.0" encoding="utf-8"?>\n<instance/>',
                                                software_type='default'),
                                      follow_redirects=True))

    while self.app.get('/isSRReady').data == "2":
      time.sleep(2)
    self.assertEqual(self.app.get('/isSRReady').data, "1")

    # Run instance deployment 3 times
    runInstanceWithLock(self.app.config)
    runInstanceWithLock(self.app.config)
    result = runInstanceWithLock(self.app.config)
    # result is True if returncode is 0 (i.e "deployed and promise passed")
    self.assertTrue(result)


  def test_dynamicParametersReading(self):
    """Test if the value of a parameter can change in the flask application
    only by changing the value of slapos.cfg config file. This can happen when
    slapgrid processes the webrunner's partition.
    """
    config_file = os.path.join(self.app.config['etc_dir'], 'slapos-test.cfg')
    runner_config_old = os.environ['RUNNER_CONFIG']
    os.environ['RUNNER_CONFIG'] = config_file
    open(config_file, 'w').write("[section]\nvar=value")
    config = self.app.config
    self.assertEqual(config['var'], "value")
    open(config_file, 'w').write("[section]\nvar=value_changed")
    self.assertEqual(config['var'], "value_changed")
    # cleanup
    os.environ['RUNNER_CONFIG'] = runner_config_old


class PrintStringIO(StringIO):
  def write(self, data):
    StringIO.write(self, data)
    print data

def main():
  """
  Function meant to be run by erp5testnode.
  """
  args = parseArguments()
  master = taskdistribution.TaskDistributor(args.master_url)
  test_suite_title = args.test_suite_title or args.test_suite
  revision = args.revision

  SlaprunnerTestCase.setUpClass(
    key_file=args.key_file,
    cert_file=args.cert_file,
    server_url=args.server_url,
    computer_id=args.computer_id,
    partition_id=args.partition_id)

  test_result = master.createTestResult(revision, [test_suite_title],
    args.test_node_title, True, test_suite_title, args.project_title)

  if test_result is None:
    # Thereis nothing to run here, all tests are been running by
    # some other node.
    return
  test_line = test_result.start()

  start_time = time.time()

  stderr = PrintStringIO()
  suite = unittest.TestLoader().loadTestsFromTestCase(SlaprunnerTestCase)
  test_result = unittest.TextTestRunner(verbosity=2, stream=stderr).run(suite)

  test_duration = time.time() - start_time
  test_line.stop(stderr=stderr.getvalue(),
                  test_count=test_result.testsRun,
                  error_count=len(test_result.errors),
                  failure_count=len(test_result.failures) + len(test_result.unexpectedSuccesses),
                  skip_count=len(test_result.skipped),
                  duration=test_duration)

def runStandaloneUnitTest():
  """
  Run unit tests without erp5testnode."
  """
  unittest.main(module=__name__)
