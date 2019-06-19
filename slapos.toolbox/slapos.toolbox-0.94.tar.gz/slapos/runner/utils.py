# -*- coding: utf-8 -*-
# vim: set et sts=2:
# pylint: disable-msg=W0311,C0301,C0103,C0111,W0141,W0142

import ConfigParser
import datetime
import json
import logging
import md5
import os
import sup_process
import re
import shutil
import stat
import thread
import time
import urllib
import xmlrpclib
from xml.dom import minidom

import xml_marshaller
from flask import jsonify

from slapos.runner.gittools import cloneRepo

from slapos.runner.process import Popen
# from slapos.htpasswd import HtpasswdFile
from passlib.apache import HtpasswdFile
import slapos.slap
from slapos.grid.utils import md5digest

logger = logging.getLogger('slaprunner')

TRUE_VALUES = (1, '1', True, 'true', 'True')

html_escape_table = {
  "&": "&amp;",
  '"': "&quot;",
  "'": "&apos;",
  ">": "&gt;",
  "<": "&lt;",
}

def getBuildAndRunParams(config):
  json_file = os.path.join(config['etc_dir'], 'config.json')
  json_params = json.load(open(json_file))
  return json_params


def saveBuildAndRunParams(config, params):
  """XXX-Nico parameters have to be correct.
  Works like that because this function do not care
  about how you got the parameters"""
  json_file = os.path.join(config['etc_dir'], 'config.json')
  open(json_file, "w").write(json.dumps(params))


def html_escape(text):
  """Produce entities within text."""
  return "".join(html_escape_table.get(c, c) for c in text)

def getSession(config):
  """
  Get the session data of current user.
  Returns:
    a list of user information or None if the file does not exist.
  """
  user_path = os.path.join(config['etc_dir'], '.htpasswd')
  if os.path.exists(user_path):
    return open(user_path).read().split(';')

def checkUserCredential(config, username, password):
  htpasswdfile = os.path.join(config['etc_dir'], '.htpasswd')
  if not os.path.exists(htpasswdfile):
    return False
  passwd = HtpasswdFile(htpasswdfile)
  return passwd.check_password(username, password)

def updateUserCredential(config, username, password):
  """
  Save account information for the current user

  """
  if username and password:
    htpasswdfile = os.path.join(config['etc_dir'], '.htpasswd')
    passwd = HtpasswdFile(htpasswdfile)
    passwd.set_password(username, password)
    passwd.save()
    return True

  return False


def getRcode(config):
  parser = ConfigParser.ConfigParser()
  try:
    parser.read(config['knowledge0_cfg'])
    return parser.get('public', 'recovery-code')
  except (ConfigParser.NoSectionError, IOError) as e:
    return None

def getUsernameList(config):
  htpasswdfile = os.path.join(config['etc_dir'], '.htpasswd')
  if os.path.exists(htpasswdfile):
    passwd = HtpasswdFile(htpasswdfile)
    return passwd.users()

  return []

def createNewUser(config, name, passwd):
  htpasswdfile = os.path.join(config['etc_dir'], '.htpasswd')
  try:
    htpasswd = HtpasswdFile(htpasswdfile, new=(not os.path.exists(htpasswdfile)))
    htpasswd.set_password(name, passwd)
    htpasswd.save()
  except IOError:
    return False
  return True

def getCurrentSoftwareReleaseProfile(config):
  """
  Returns used Software Release profile as a string.
  """
  try:
    software_folder = open(
        os.path.join(config['etc_dir'], ".project")).read().rstrip()
    return realpath(
        config, os.path.join(software_folder, config['software_profile']))
  # XXXX No Comments
  except IOError:
    return ''


def requestInstance(config, software_type=None):
  """
  Request the main instance of our environment
  """
  software_type_path = os.path.join(config['etc_dir'], ".software_type.xml")
  if software_type:
    # Write it to conf file for later use
    open(software_type_path, 'w').write(software_type)
  elif os.path.exists(software_type_path):
    software_type = open(software_type_path).read().rstrip()
  else:
    software_type = 'default'

  slap = slapos.slap.slap()
  profile = getCurrentSoftwareReleaseProfile(config)
  slap.initializeConnection(config['master_url'])

  param_path = os.path.join(config['etc_dir'], ".parameter.xml")
  xml_result = readParameters(param_path)
  partition_parameter_kw = None
  if type(xml_result) != type('') and 'instance' in xml_result:
    partition_parameter_kw = xml_result['instance']

  return slap.registerOpenOrder().request(
      profile,
      partition_reference=getSoftwareReleaseName(config),
      partition_parameter_kw=partition_parameter_kw,
      software_type=software_type,
      filter_kw=None,
      state=None,
      shared=False)


def updateProxy(config):
  """
  Configure Slapos Node computer and partitions.
  Send current Software Release to Slapproxy for compilation and deployment.
  """
  startProxy(config)
  if not os.path.exists(config['instance_root']):
    os.mkdir(config['instance_root'])
  slap = slapos.slap.slap()
  profile = getCurrentSoftwareReleaseProfile(config)

  slap.initializeConnection(config['master_url'])
  slap.registerSupply().supply(profile, computer_guid=config['computer_id'])
  computer = slap.registerComputer(config['computer_id'])
  prefix = 'slappart'
  slap_config = {
    'address': config['ipv4_address'],
    'instance_root': config['instance_root'],
    'netmask': '255.255.255.255',
    'partition_list': [],
    'reference': config['computer_id'],
    'software_root': config['software_root']
  }

  for i in xrange(0, int(config['partition_amount'])):
    partition_reference = '%s%s' % (prefix, i)
    partition_path = os.path.join(config['instance_root'], partition_reference)
    if not os.path.exists(partition_path):
      os.mkdir(partition_path)
    os.chmod(partition_path, 0750)
    slap_config['partition_list'].append({
                                           'address_list': [
                                              {
                                                'addr': config['ipv4_address'],
                                                'netmask': '255.255.255.255'
                                              }, {
                                                'addr': config['ipv6_address'],
                                                'netmask': 'ffff:ffff:ffff::'
                                              },
                                           ],
                                           'path': partition_path,
                                           'reference': partition_reference,
                                           'tap': {'name': partition_reference}})
  computer.updateConfiguration(xml_marshaller.xml_marshaller.dumps(slap_config))
  return True


def updateInstanceParameter(config, software_type=None):
  """
  Reconfigure Slapproxy to re-deploy current Software Instance with parameters.

  Args:
    config: Slaprunner configuration.
    software_type: reconfigure Software Instance with software type.
  """
  time.sleep(1)
  if not (updateProxy(config) and requestInstance(config, software_type)):
    return False


def startProxy(config):
  """Start Slapproxy server"""
  if sup_process.isRunning(config, 'slapproxy'):
    return
  try:
    return sup_process.runProcess(config, "slapproxy")
  except xmlrpclib.Fault:
    pass
  time.sleep(4)


def stopProxy(config):
  """Stop Slapproxy server"""
  return sup_process.stopProcess(config, "slapproxy")


def removeProxyDb(config):
  """Remove Slapproxy database, this is used to initialize proxy for example when
    configuring new Software Release"""
  if os.path.exists(config['database_uri']):
    os.unlink(config['database_uri'])


def isSoftwareRunning(config):
  """
    Return True if slapos is still running and false if slapos if not
  """
  return sup_process.isRunning(config, 'slapgrid-sr')


def slapgridResultToFile(config, step, returncode, datetime):
  filename = step + "_info.json"
  file = os.path.join(config['runner_workdir'], filename)
  result = {'last_build':datetime, 'success':returncode}
  open(file, "w").write(json.dumps(result))


def getSlapgridResult(config, step):
  filename = step + "_info.json"
  file = os.path.join(config['runner_workdir'], filename)
  if os.path.exists(file):
    result = json.loads(open(file, "r").read())
  else:
    result = {'last_build': 0, 'success':-1}
  return result


def waitProcess(config, process, step):
  process.wait()
  date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  slapgridResultToFile(config, step, process.returncode, date)

def runSlapgridWithLock(config, step, process_name, lock=False):
  """
  * process_name is the name of the process given to supervisord, which will
    run the software or the instance
  * step is one of ('software', 'instance')
  * lock allows to make this function asynchronous or not
  """
  if sup_process.isRunning(config, process_name):
    return 1

  root_folder = config["%s_root" % step]
  log_file = config["%s_log" % step]

  if not os.path.exists(root_folder):
    os.mkdir(root_folder)

  # XXX Hackish and unreliable
  if os.path.exists(log_file):
    os.remove(log_file)
  if not updateProxy(config):
    return 1
  if step == 'instance' and not requestInstance(config):
    return 1
  try:
    sup_process.runProcess(config, process_name)
    if lock:
      sup_process.waitForProcessEnd(config, process_name)
    #Saves the current compile software for re-use
    if step == 'software':
      config_SR_folder(config)
    return sup_process.returnCode(config, process_name)
  except xmlrpclib.Fault:
    return 1


def runSoftwareWithLock(config, lock=False):
  """
    Use Slapgrid to compile current Software Release and wait until
    compilation is done
  """
  return runSlapgridWithLock(config, 'software', 'slapgrid-sr', lock)


def runInstanceWithLock(config, lock=False):
  """
    Use Slapgrid to deploy current Software Release and wait until
    deployment is done.
  """
  return runSlapgridWithLock(config, 'instance', 'slapgrid-cp', lock)


def config_SR_folder(config):
  """Create a symbolik link for each folder in software folder. That allows
    the user to customize software release folder"""
  config_name = 'slaprunner.config'
  def link_to_folder(name, folder):
    destination = os.path.join(config['software_link'], name)
    source = os.path.join(config['software_root'], folder)
    cfg = os.path.join(destination, config_name)
        #create symlink
    if os.path.lexists(destination):
      os.remove(destination)
    os.symlink(source, destination)
        #write config file
    if os.path.exists(source):
      with open(cfg, 'w') as cf:
        cf.write(current_project + '#' + folder)

  # First create the link for current project
  with open(os.path.join(config['etc_dir'], ".project")) as f:
    current_project = f.read().strip().rstrip('/')
  profile = getCurrentSoftwareReleaseProfile(config)
  name = current_project.split('/')[-1]
  md5sum = md5digest(profile)
  link_to_folder(name, md5sum)
  # check other links
  software_link_list = []
  for path in os.listdir(config['software_link']):
    cfg_path = os.path.join(config['software_link'], path, config_name)
    if os.path.exists(cfg_path):
      cfg = open(cfg_path).read().split("#")
      if len(cfg) != 2:
        continue  # there is a broken config file
      software_link_list.append(cfg[1])
  if os.path.exists(config['software_root']):
    folder_list = os.listdir(config['software_root'])
  else:
    return
  if not folder_list:
    return
  for folder in folder_list:
    if folder in software_link_list:
      continue  # this folder is already registered
    else:
      link_to_folder(folder, folder)

def loadSoftwareRList(config):
  """Return list (of dict) of Software Release from symbolik SR folder"""
  sr_list = []
  config_name = 'slaprunner.config'
  for path in os.listdir(config['software_link']):
    cfg_path = os.path.join(config['software_link'], path, config_name)
    if os.path.exists(cfg_path):
      cfg = open(cfg_path).read().split("#")
      if len(cfg) != 2:
        continue  # there is a broken config file
      sr_list.append(dict(md5=cfg[1], path=cfg[0], title=path))
  return sr_list


def isInstanceRunning(config):
  """
    Return True if slapos is still running and False otherwise
  """
  return sup_process.isRunning(config, 'slapgrid-cp')


def getProfilePath(projectDir, profile):
  """
  Return the path of the current Software Release `profile`

  Args:
    projectDir: Slaprunner workspace location.
    profile: file to search into the workspace.

  Returns:
    String, path of current Software Release profile
  """
  if not os.path.exists(os.path.join(projectDir, ".project")):
    return False
  projectFolder = open(os.path.join(projectDir, ".project")).read()
  return os.path.join(projectFolder, profile)


def getSlapStatus(config):
  """Return all Slapos Partitions with associate information"""
  slap = slapos.slap.slap()
  slap.initializeConnection(config['master_url'])
  partition_list = []
  computer = slap.registerComputer(config['computer_id'])
  try:
    for partition in computer.getComputerPartitionList():
      # Note: Internal use of API, as there is no reflexion interface in SLAP
      partition_list.append((partition.getId(), partition._connection_dict.copy()))
  except Exception:
    pass
  if partition_list:
    for i in xrange(0, int(config['partition_amount'])):
      slappart_id = '%s%s' % ("slappart", i)
      if not [x[0] for x in partition_list if slappart_id == x[0]]:
        partition_list.append((slappart_id, []))
  return partition_list


def svcStopAll(config):
  """Stop all Instance processes on this computer"""
  try:
    return Popen([config['slapos'], 'node', 'supervisorctl', '--cfg', config['configuration_file_path'],
                  'stop', 'all']).communicate()[0]
  except:
    pass

def svcStartAll(config):
  """Start all Instance processes on this computer"""
  try:
    return Popen([config['slapos'], 'node', 'supervisorctl', '--cfg', config['configuration_file_path'],
                  'start', 'all']).communicate()[0]
  except:
    pass

def removeInstanceRootDirectory(config):
  """Clean instance directory"""
  if os.path.exists(config['instance_root']):
    for instance_directory in os.listdir(config['instance_root']):
      instance_directory = os.path.join(config['instance_root'], instance_directory)
      # XXX: hardcoded
      if stat.S_ISSOCK(os.stat(instance_directory).st_mode) or os.path.isfile(instance_directory):
        # Ignore non-instance related files
        continue
      for root, dirs, _ in os.walk(instance_directory):
        for fname in dirs:
          fullPath = os.path.join(root, fname)
          if not os.access(fullPath, os.W_OK):
            # Some directories may be read-only, preventing to remove files in it
            os.chmod(fullPath, 0744)
      shutil.rmtree(instance_directory)

def removeCurrentInstance(config):
  if isInstanceRunning(config):
    return "Instantiation in progress, cannot remove instance"

  # Stop all processes
  svcStopAll(config)
  if stopProxy(config):
    removeProxyDb(config)
    startProxy(config)
  else:
    return "Something went wrong when trying to stop slapproxy."

  # Remove Instance directory and data related to the instance
  try:
    removeInstanceRootDirectory(config)
    param_path = os.path.join(config['etc_dir'], ".parameter.xml")
    if os.path.exists(param_path):
      os.remove(param_path)
  except IOError:
    return "The filesystem couldn't been cleaned properly"
  return True


def getSvcStatus(config):
  """Return all Softwares Instances process Information"""
  result = Popen([config['slapos'], 'node', 'supervisorctl', '--cfg', config['configuration_file_path'],
                  'status']).communicate()[0]
  regex = "(^unix:.+\.socket)|(^error:)|(^watchdog).*$"
  supervisord = []
  for item in result.split('\n'):
    if item.strip() != "":
      if re.search(regex, item, re.IGNORECASE) is None:
        supervisord.append(re.split('[\s,]+', item))
  return supervisord


def getSvcTailProcess(config, process):
  """Get log for the specified process

  Args:
    config: Slaprunner configuration
    process: process name. this value is passed to supervisord.
  Returns:
    a string that contains the log of the process.
  """
  return Popen([config['slapos'], 'node', 'supervisorctl', '--cfg', config['configuration_file_path'],
                "tail", process]).communicate()[0]


def svcStartStopProcess(config, process, action):
  """Send start or stop process command to supervisord

  Args:
    config: Slaprunner configuration.
    process: process to start or stop.
    action: current state which is used to generate the new process state.
  """
  cmd = {
    'RESTART': 'restart',
    'STOPPED': 'start',
    'RUNNING': 'stop',
    'EXITED': 'start',
    'STOP': 'stop'
  }
  return Popen([config['slapos'], 'node', 'supervisorctl', '--cfg', config['configuration_file_path'],
                cmd[action], process]).communicate()[0]


def listFolder(config, path):
  """Return the list of folder into path

  Agrs:
    path: path of the directory to list
  Returns:
    a list that contains each folder name.
  """
  folderList = []
  folder = realpath(config, path)
  if folder:
    path_list = sorted(os.listdir(folder), key=str.lower)
    for elt in path_list:
      if os.path.isdir(os.path.join(folder, elt)):
        folderList.append(elt)
  return folderList


def configNewSR(config, projectpath):
  """Configure a Software Release as current Software Release

  Args:
    config: slaprunner configuration
    projectpath: path of the directory that contains the software realease to configure
  Returns:
    True if all is done well, otherwise return false.
  """
  folder = realpath(config, projectpath)
  if folder:
    sup_process.stopProcess(config, 'slapgrid-cp')
    sup_process.stopProcess(config, 'slapgrid-sr')
    logger.warning("User opened a new SR. Removing all instances...")
    removeCurrentInstance(config)
    open(os.path.join(config['etc_dir'], ".project"), 'w').write(projectpath)
    return True
  else:
    return False


def newSoftware(folder, config, session):
  """
  Create a new Software Release folder with default profiles

  Args:
    folder: directory of the new software release
    config: slraprunner configuration
    session: Flask session directory"""
  json = ""
  code = 0
  basedir = config['etc_dir']
  try:
    folderPath = realpath(config, folder, check_exist=False)
    if folderPath and not os.path.exists(folderPath):
      os.mkdir(folderPath)
      #load software.cfg and instance.cfg from https://lab.nexedi.com
      software = "https://lab.nexedi.com/nexedi/slapos/raw/master/software/lamp-template/software.cfg"
      softwareContent = ""
      try:
        softwareContent = urllib.urlopen(software).read()
      except:
        #Software.cfg and instance.cfg content will be empty
        pass
      open(os.path.join(folderPath, config['software_profile']), 'w').write(softwareContent)
      open(os.path.join(folderPath, config['instance_profile']), 'w').write("")
      open(os.path.join(basedir, ".project"), 'w').write(folder + "/")
      #Clean sapproxy Database
      stopProxy(config)
      removeProxyDb(config)
      startProxy(config)
      #Stop runngin process and remove existing instance
      logger.warning("User created a new SR. Removing all instances...")
      removeCurrentInstance(config)
      session['title'] = getProjectTitle(config)
      code = 1
    else:
      json = "Bad folder or Directory '%s' already exist, please enter a new name for your software" % folder
  except Exception as e:
    json = "Can not create your software, please try again! : %s " % e
    if os.path.exists(folderPath):
      shutil.rmtree(folderPath)
  return jsonify(code=code, result=json)


def checkSoftwareFolder(path, config):
  """Check id `path` is a valid Software Release folder"""
  realdir = realpath(config, path)
  if realdir and os.path.exists(os.path.join(realdir, config['software_profile'])):
    return jsonify(result=path)
  return jsonify(result="")


def getProjectTitle(config):
  """Generate the name of the current software Release (for slaprunner UI)"""
  conf = os.path.join(config['etc_dir'], ".project")
  # instance_name is optional parameter
  instance_name = config.get('instance_name')
  if instance_name:
    instance_name = '%s - ' % instance_name
  if os.path.exists(conf):
    project = open(conf, "r").read().split("/")
    software = project[-2]
    return '%s%s (%s)' % (instance_name, software, '/'.join(project[:-2]))
  return "%sNo Profile" % instance_name


def getSoftwareReleaseName(config):
  """Get the name of the current Software Release"""
  sr_profile = os.path.join(config['etc_dir'], ".project")
  if os.path.exists(sr_profile):
    project = open(sr_profile, "r").read().split("/")
    software = project[-2]
    return software.replace(' ', '_')
  return None

def removeSoftwareRootDirectory(config, md5, folder_name):
  """
  Removes all content in the filesystem of the software release specified by md5

  Args:
    config: slaprunner configuration
    folder_name: the link name given to the software release
    md5: the md5 filename given by slapgrid to SR folder
  """
  path = os.path.join(config['software_root'], md5)
  linkpath = os.path.join(config['software_link'], folder_name)
  if not os.path.exists(path):
    return (0, "Cannot remove software Release: No such file or directory")
  if not os.path.exists(linkpath):
    return (0, "Cannot remove software Release: No such file or directory %s" %
                    ('software_root/' + folder_name))
  os.unlink(linkpath)
  shutil.rmtree(path)
  return

def removeSoftwareByName(config, md5, folder_name):
  """
  Removes a software release specified by its md5 and its name from the webrunner.
  If the software release is the one of the current running instance, then
  the instance should be stopped.

  Args:
    config: slaprunner configuration
    folder_name: the link name given to the software release
    md5: the md5 filename given by slapgrid to SR folder
  """
  if isSoftwareRunning(config) or isInstanceRunning(config):
    return (0, "Software installation or instantiation in progress, cannot remove")

  if getSoftwareReleaseName(config) == folder_name:
    logger.warning("User removed the SR currently used. Removing all instances...")
    removeCurrentInstance(config)

  result = removeSoftwareRootDirectory(config, md5, folder_name)
  if result is not None:
    return result
  return 1, loadSoftwareRList(config)


def tail(f, lines=20):
  """
  Returns the last `lines` lines of file `f`. It is an implementation of tail -f n.
  """
  BUFSIZ = 1024
  f.seek(0, 2)
  bytes = f.tell()
  size = lines + 1
  block = -1
  data = []
  while size > 0 and bytes > 0:
      if bytes - BUFSIZ > 0:
          # Seek back one whole BUFSIZ
          f.seek(block * BUFSIZ, 2)
          # read BUFFER
          data.insert(0, f.read(BUFSIZ))
      else:
          # file too small, start from begining
          f.seek(0, 0)
          # only read what was not read
          data.insert(0, f.read(bytes))
      linesFound = data[0].count('\n')
      size -= linesFound
      bytes -= BUFSIZ
      block -= 1
  return '\n'.join(''.join(data).splitlines()[-lines:])


def readFileFrom(f, lastPosition, limit=20000):
  """
  Returns the last lines of file `f`, from position lastPosition.
  and the last position
  limit = max number of characters to read
  """
  BUFSIZ = 1024
  f.seek(0, 2)
  # XXX-Marco do now shadow 'bytes'
  bytes = f.tell()
  block = -1
  data = ""
  length = bytes
  truncated = False  # True if a part of log data has been truncated
  if (lastPosition <= 0 and length > limit) or (length - lastPosition > limit):
    lastPosition = length - limit
    truncated = True
  size = bytes - lastPosition
  while bytes > lastPosition:
    if abs(block * BUFSIZ) <= size:
      # Seek back one whole BUFSIZ
      f.seek(block * BUFSIZ, 2)
      data = f.read(BUFSIZ) + data
    else:
      margin = abs(block * BUFSIZ) - size
      if length < BUFSIZ:
        f.seek(0, 0)
      else:
        seek = block * BUFSIZ + margin
        f.seek(seek, 2)
      data = f.read(BUFSIZ - margin) + data
    bytes -= BUFSIZ
    block -= 1
  f.close()
  return {
    'content': data,
    'position': length,
    'truncated': truncated
  }


def isText(file):
  """Return True if the mimetype of file is Text"""
  if not os.path.exists(file):
    return False
  text_range = ''.join(map(chr, [7, 8, 9, 10, 12, 13, 27] + range(0x20, 0x100)))
  is_binary_string = lambda bytes: bool(bytes.translate(None, text_range))
  try:
    return not is_binary_string(open(file).read(1024))
  except:
    return False


def md5sum(file):
  """Compute md5sum of `file` and return hexdigest value"""
  # XXX-Marco: returning object or False boolean is an anti-pattern. better to return object or None
  if os.path.isdir(file):
    return False
  try:
    fh = open(file, 'rb')
    m = md5.md5()
    while True:
      data = fh.read(8192)
      if not data:
        break
      m.update(data)
    return m.hexdigest()
  except:
    return False


def realpath(config, path, check_exist=True):
  """
  Get realpath of path or return False if user is not allowed to access to
  this file.
  """
  split_path = path.split('/')
  key = split_path[0]
  virtual_path_list = ('software_root', 'instance_root', 'workspace',
    'runner_workdir', 'software_link')
  if key not in virtual_path_list:
    return ''
  allow_list = {path: config[path] for path in virtual_path_list if path in config}
  del split_path[0]
  path = os.path.join(allow_list[key], *split_path)
  if check_exist:
    if os.path.exists(path):
      return path
    else:
      return ''
  else:
    return path


def readParameters(path):
  """Read Instance parameters stored into a local file.

  Agrs:
    path: path of the xml file that contains parameters

  Return:
    a dictionary of instance parameters."""
  if os.path.exists(path):
    try:
      xmldoc = minidom.parse(path)
      obj = {}
      for elt in xmldoc.childNodes:
        sub_obj = {}
        for subnode in elt.childNodes:
          if subnode.nodeType != subnode.TEXT_NODE:
            sub_obj[str(subnode.getAttribute('id'))] = subnode.childNodes[0].data  # .decode('utf-8').decode('utf-8')
            obj[str(elt.tagName)] = sub_obj
      return obj
    except Exception, e:
      return str(e)
  else:
    return "No such file or directory: %s" % path

def isSoftwareReleaseCompleted(config):
  software_name = getSoftwareReleaseName(config)
  if software_name is None:
    return False
  elif os.path.exists(os.path.join(config['runner_workdir'],
      'softwareLink', software_name, '.completed')):
    return True
  else:
    return False

def isSoftwareReleaseReady(config):
  """Return 1 if the Software Release has
  correctly been deployed, 0 if not,
  and 2 if it is currently deploying"""
  auto_deploy = config['auto_deploy'] in TRUE_VALUES
  auto_run = config['autorun'] in TRUE_VALUES
  project = os.path.join(config['etc_dir'], '.project')
  if not ( os.path.exists(project) and (auto_run or auto_deploy) ):
    return "0"
  updateInstanceParameter(config)
  if isSoftwareReleaseCompleted(config):
    if auto_run:
      runSlapgridUntilSuccess(config, 'instance')
    return "1"
  else:
    if isSoftwareRunning(config):
      return "2"
    elif auto_deploy:
      runSoftwareWithLock(config)
      if auto_run:
        runSlapgridUntilSuccess(config, 'instance')
      return "2"
    else:
      return "0"


def cloneDefaultGit(config):
  """Test if the default git has been downloaded yet
  If not, download it in read-only mode"""
  default_git = os.path.join(config['runner_workdir'],
    'project', 'default_repo')
  if not os.path.exists(default_git):
    data = {'path': default_git,
            'repo': config['default_repo'],
    }
    cloneRepo(data)


def buildAndRun(config):
  runSoftwareWithLock(config)
  runInstanceWithLock(config)


def runSlapgridUntilSuccess(config, step):
  """Run slapos several times,
  in the maximum of the constant MAX_RUN_~~~~"""
  params = getBuildAndRunParams(config)
  if step == "instance":
    max_tries = (params['max_run_instance'] if params['run_instance'] else 0)
    runSlapgridWithLock = runInstanceWithLock
  elif step == "software":
    max_tries = (params['max_run_software'] if params['run_software'] else 0)
    runSlapgridWithLock = runSoftwareWithLock
  else:
    return -1
  counter_file = os.path.join(config['runner_workdir'], '.turn-left')
  open(counter_file, 'w+').write(str(max_tries))
  counter = max_tries
  slapgrid = True
  # XXX-Nico runSoftwareWithLock can return 0 or False (0==False)
  while counter > 0:
    counter -= 1
    slapgrid = runSlapgridWithLock(config, lock=True)
    # slapgrid == 0 because EXIT_SUCCESS == 0
    if slapgrid == 0:
      break
    times_left = int(open(counter_file).read()) - 1
    if times_left > 0 :
      open(counter_file, 'w+').write(str(times_left))
      counter = times_left
    else :
      counter = 0
  max_tries -= counter
  # run instance only if we are deploying the software release,
  # if it is defined so, and sr is correctly deployed
  if step == "software" and params['run_instance'] and slapgrid == 0:
    return (max_tries, runSlapgridUntilSuccess(config, "instance"))
  else:
    return max_tries


def setupDefaultSR(config):
  """If a default_sr is in the parameters,
  and no SR is deployed yet, setup it
  also run SR and Instance if required"""
  project = os.path.join(config['etc_dir'], '.project')
  if not os.path.exists(project) and config['default_sr'] != '':
    configNewSR(config, config['default_sr'])
  if config['auto_deploy']:
    thread.start_new_thread(buildAndRun, (config,))


def setMiniShellHistory(config, command):
  history_max_size = 10
  command = command + "\n"
  history_file = config['minishell_history_file']
  if os.path.exists(history_file):
    history = open(history_file, 'r').readlines()
    if len(history) >= history_max_size:
      del history[0]
  else:
    history = []
  history.append(command)
  open(history_file, 'w+').write(''.join(history))
