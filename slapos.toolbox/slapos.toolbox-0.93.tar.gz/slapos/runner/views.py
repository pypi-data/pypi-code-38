# -*- coding: utf-8 -*-
# vim: set et sts=2:
# pylint: disable-msg=W0311,C0301,C0103,C0111

import codecs
import json
import os
import shutil
import subprocess
import sup_process
import thread
import urllib

from flask import (Flask, request, redirect, url_for, render_template,
                   g, flash, jsonify, session, abort, send_file)

import slapos
from slapos.runner.utils import (checkSoftwareFolder, configNewSR, checkUserCredential,
                                 createNewUser, getBuildAndRunParams,
                                 getProfilePath, getSlapgridResult,
                                 html_escape,
                                 listFolder, getBuildAndRunParams,
                                 getProjectTitle, getRcode, updateUserCredential,
                                 getSlapStatus, getSvcStatus,
                                 getSvcTailProcess, getUsernameList, isInstanceRunning,
                                 isSoftwareRunning, isSoftwareReleaseReady, isText,
                                 loadSoftwareRList, md5sum, newSoftware,
                                 readFileFrom, readParameters, realpath,
                                 removeCurrentInstance,
                                 removeSoftwareByName, runSlapgridUntilSuccess,
                                 saveBuildAndRunParams,
                                 setMiniShellHistory,
                                 stopProxy,
                                 svcStartStopProcess, svcStartAll, svcStopAll, tail,
                                 updateInstanceParameter)

from git import GitCommandError
from slapos.runner.fileBrowser import FileBrowser
from slapos.runner.gittools import (cloneRepo, gitStatus, switchBranch,
                                    addBranch, getDiff, gitCommit, gitPush,
                                    gitPull, updateGitConfig, safeResult)


app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024
file_request = FileBrowser(app.config)

import logging
logger = logging.getLogger('slaprunner')

def login_redirect(*args, **kwargs):
  return redirect(url_for('login'))


@app.before_request
def before_request():
  if request.path.startswith('/static') \
    or request.path == '/isSRReady':
    return
  """
  account = getSession(app.config)
  if account:
    session['title'] = getProjectTitle(app.config)
  else:
    session['title'] = "No account is defined"
    if request.path != "/setAccount" and request.path != "/configAccount":
      return redirect(url_for('setAccount'))
  """
  session['title'] = getProjectTitle(app.config)
  g.instance_monitoring_url =  app.config['instance_monitoring_url']

# general views
def home():
  return render_template('index.html')


# general views
def browseWorkspace():
  return render_template('workspace.html')


@app.route("/login")
def login():
  return render_template('login.html')


@app.route("/setAccount")
def setAccount():
  """account = getSession(app.config)
  if not account:
    return render_template('account.html')
  return redirect(url_for('login'))"""


def myAccount():
  # account = getSession(app.config)
  git_user_path = os.path.join(app.config['etc_dir'], '.git_user')
  name = email = ""
  if os.path.exists(git_user_path):
    with open(git_user_path, 'r') as gfile:
      name, email = gfile.read().split(';')
  return render_template(
    'account.html',
    username_list=getUsernameList(app.config),
    email=email,
    name=name.decode('utf-8'),
    params=getBuildAndRunParams(app.config))


def getSlapgridParameters():
  return jsonify(getBuildAndRunParams(app.config))


def manageRepository():
  public_key = open(app.config['public_key']).read()
  account = [] #getSession(app.config)
  git_user_path = os.path.join(app.config['etc_dir'], '.git_user')
  name = email = ""
  if os.path.exists(git_user_path):
    with codecs.open(git_user_path, 'r', encoding='utf-8') as gfile:
      name, email = gfile.read().split(';')
  return render_template('manageRepository.html', workDir='workspace',
            project=listFolder(app.config, 'workspace'),
            public_key=public_key, name=name.decode('utf-8'),
            email=email)


@app.route("/doLogin", methods=['POST'])
def doLogin():
  #XXX Now has to check the .htpasswd if we want to warn
  #the user that he misspelled his name/password
  return jsonify(code=1, result="")


# software views
def editSoftwareProfile():
  profile = getProfilePath(app.config['etc_dir'], app.config['software_profile'])
  if profile == "":
    flash('Error: can not open profile, please select your project first')
  return render_template('updateSoftwareProfile.html', workDir='workspace',
      profile=profile, projectList=listFolder(app.config, 'workspace'))


def inspectSoftware():
  return render_template('runResult.html', softwareRoot='software_link/',
                         softwares=loadSoftwareRList(app.config))


#remove content of compiled software release
def removeSoftware():
  if isSoftwareRunning(app.config) or isInstanceRunning(app.config):
    flash('Software installation or instantiation in progress, cannot remove')
  elif os.path.exists(app.config['software_root']):
    svcStopAll(app.config)
    shutil.rmtree(app.config['software_root'])
    for link in os.listdir(app.config['software_link']):
      os.remove(os.path.join(app.config['software_link'], link))
    flash('Software removed')
  return redirect(url_for('inspectSoftware'))


def runSoftwareProfile():
  thread.start_new_thread(runSlapgridUntilSuccess, (app.config, "software"))
  return jsonify(result=True)


# instance views
def editInstanceProfile():
  profile = getProfilePath(app.config['etc_dir'], app.config['instance_profile'])
  if profile == "":
    flash('Error: can not open instance profile for this Software Release')
  return render_template('updateInstanceProfile.html', workDir='workspace',
      profile=profile, projectList=listFolder(app.config, 'workspace'))


# get status of all computer partitions and process state
def inspectInstance():
  if os.path.exists(app.config['instance_root']):
    file_path = 'instance_root'
    supervisor = getSvcStatus(app.config)
  else:
    file_path = ''
    supervisor = []
  if "application/json" in request.accept_mimetypes.best:
    result_list = []
    for service in supervisor:
      result_list.append({
        'service_name': service[0],
        'status': service[1],
      })
    return jsonify(result_list)
  return render_template('instanceInspect.html',
                         file_path=file_path,
                         supervisor=supervisor,
                         slap_status=getSlapStatus(app.config),
                         partition_amount=app.config['partition_amount'])

def getConnectionParameter(partition_reference):
  """
  Return connection parameters of a partition.
  """
  slap = slapos.slap.slap()
  slap.initializeConnection(app.config['master_url'])
  partition = slap.registerComputerPartition(app.config['computer_id'], partition_reference)
  return jsonify(partition.getConnectionParameterDict())
app.add_url_rule("/getConnectionParameter/<partition_reference>", 'getConnectionParameter', getConnectionParameter, methods=['GET'])

#Reload instance process ans returns new value to ajax
def supervisordStatus():
  result = getSvcStatus(app.config)
  if not result:
    return jsonify(code=0, result="")
  # XXX-Marco -> template
  html = "<tr><th>Partition and Process name</th><th>Status</th><th>Process PID </th><th> UpTime</th><th></th></tr>"
  for item in result:
    html += "<tr>"
    html += "<td  class='first'><b><a href='" + url_for('tailProcess', process=item[0]) + "'>" + item[0] + "</a></b></td>"
    html += "<td align='center'><a href='" + url_for('startStopProccess', process=item[0], action=item[1]) + "'>" + item[1] + "</a></td>"
    html += "<td align='center'>" + item[3] + "</td><td>" + item[5] + "</td>"
    html += "<td align='center'><a href='" + url_for('startStopProccess', process=item[0], action='RESTART') + "'>Restart</a></td>"
    html += "</tr>"
  return jsonify(code=1, result=html)


def removeInstance():
  logger.warning("User clicked on 'Destroy All Services'. Removing all instances...")
  result = removeCurrentInstance(app.config)
  if isinstance(result, str):
    flash(result)
  return redirect(url_for('inspectInstance'))


def runInstanceProfile():
  if not os.path.exists(app.config['instance_root']):
    os.mkdir(app.config['instance_root'])
  thread.start_new_thread(runSlapgridUntilSuccess, (app.config, "instance"))
  return jsonify(result=True)


def viewLog():
  return render_template('viewLog.html')

def getFileLog():
  logfile = request.form.get('filename', '').encode('utf-8')
  if logfile == "instance.log":
    file_path = app.config['instance_log']
  elif logfile == "software.log":
    file_path = app.config['software_log']
  else:
    file_path = realpath(app.config, logfile)
  try:
    if not os.path.exists(file_path):
      raise IOError
    if not isText(file_path):
      content = "Can not open binary file, please select a text file!"
    if 'truncate' in request.form:
      content = tail(open(file_path), int(request.form['truncate']))
    else:
      with open(file_path) as f:
        content = f.read()
    return jsonify(code=1, result=html_escape(content))
  except:
    return jsonify(code=0, result="Warning: Log file doesn't exist yet or empty log!!")


def stopAllPartition():
  svcStopAll(app.config)
  return redirect(url_for('inspectInstance'))

def startAllPartition():
  svcStartAll(app.config)
  return redirect(url_for('inspectInstance'))

def tailProcess(process):
  return render_template('processTail.html',
      process_log=getSvcTailProcess(app.config, process), process=process)


def startStopProccess(process, action):
  svcStartStopProcess(app.config, process, action)
  return redirect(url_for('inspectInstance'))


def openProject(method):
  return render_template('projectFolder.html', method=method,
                         workDir='workspace')


def cloneRepository():
  path = realpath(app.config, request.form['name'], False)
  if not path:
    return jsonify(code=0, result="Can not access folder: Permission Denied")
  try:
    cloneRepo(request.form['repo'], path, request.form['user'], request.form['email'])
    return jsonify(code=1, result="")
  except GitCommandError, e:
    return jsonify(code=0, result=safeResult(str(e)))


def listDirectory():
  folderList = listFolder(app.config, request.form['name'])
  return jsonify(result=folderList)


def createSoftware():
  return newSoftware(request.form['folder'], app.config, session)


def checkFolder():
  return checkSoftwareFolder(request.form['path'], app.config)


def setCurrentProject():
  if configNewSR(app.config, request.form['path']):
    session['title'] = getProjectTitle(app.config)
    return jsonify(code=1, result="")
  else:
    return jsonify(code=0, result=("Can not setup this Software Release"))


def getProjectStatus():
  path = realpath(app.config, request.form['project'])
  if path:
    try:
      result, branch, isdirty = gitStatus(path)
      return jsonify(code=1, result=result, branch=branch, dirty=isdirty)
    except GitCommandError, e:
      return jsonify(code=0, result=safeResult(str(e)))
  else:
    return jsonify(code=0, result="Can not read folder: Permission Denied")


#view for current software release files
def editCurrentProject():
  project_file = os.path.join(app.config['etc_dir'], ".project")
  # XXX hardcoded default project
  project = "workspace/slapos"
  if os.path.exists(project_file):
    project = open(project_file).read()
  projectList = listFolder(app.config, 'workspace')
  if projectList:
    return render_template('softwareFolder.html', workDir='runner_workdir',
                           project=project,
                           projectList=projectList)
  else:
    flash('Please clone slapos repository, or your own repository')
    return redirect(url_for('manageRepository'))

#create file or directory
def createFile():
  path = realpath(app.config, request.form['file'], False)
  if not path:
    return jsonify(code=0, result="Error when creating your %s: Permission Denied" % request.form['type'])
  try:
    if request.form['type'] == "file":
      open(path, 'w')
    else:
      os.mkdir(path)
    return jsonify(code=1, result="")
  except Exception as e:
    return jsonify(code=0, result=str(e))


#remove file or directory
def removeFile():
  try:
    if request.form['type'] == "folder":
      shutil.rmtree(request.form['path'])
    else:
      os.remove(request.form['path'])
    return jsonify(code=1, result="")
  except Exception as e:
    return jsonify(code=0, result=str(e))


def removeSoftwareDir():
    status, message = removeSoftwareByName(app.config, request.form['md5'],
      request.form['title'])
    return jsonify(code=status, result=message)


#read file and return content to ajax
def getFileContent():
  file_path = realpath(app.config, request.form['file'])
  if file_path:
    if not isText(file_path):
      return jsonify(code=0,
            result="Can not open a binary file, please select a text file!")
    if 'truncate' in request.form:
      content = tail(codecs.open(file_path, "r", "utf_8"), int(request.form['truncate']))
      return jsonify(code=1, result=content)
    else:
      return jsonify(code=1, result=codecs.open(file_path, "r", "utf_8").read())
  else:
    return jsonify(code=0, result="Error: No such file!")


def saveFileContent():
  file_path = realpath(app.config, request.form['file'], False)
  if file_path:
    with open(file_path, 'w') as f:
      f.write(request.form['content'].encode("utf-8"))
    return jsonify(code=1, result="")
  else:
    return jsonify(code=0, result="Rejected!! Cannot access to this location.")


def changeBranch():
  path = realpath(app.config, request.form['project'])
  if path:
    try:
      if switchBranch(path, request.form['name']):
        return jsonify(code=1, result="")
      else:
        json = "This is already your active branch for this project"
        return jsonify(code=1, result=json)
    except GitCommandError, e:
      return jsonify(code=0, result=safeResult(str(e)))
  else:
    return jsonify(code=0, result="Can not read folder: Permission Denied")


def newBranch():
  path = realpath(app.config, request.form['project'])
  if path:
    try:
      if request.form['create'] == '1':
        result = addBranch(path, request.form['name'])
      else:
        result =  addBranch(path, request.form['name'], True)
      if result:
        return jsonify(code=1, result="")
      else:
        return jsonify(code=0, result="Failed to checkout to branch %s.")
    except GitCommandError, e:
      return jsonify(code=0, result=safeResult(str(e)))
  else:
    return jsonify(code=0, result="Can not read folder: Permission Denied")


def getProjectDiff():
  path = realpath(app.config, request.form['project'])
  if path:
    return jsonify(code=1, result=getDiff(path))
  else:
    return jsonify(code=0,
                  result="Error: No such file or directory. PERMISSION DENIED!")


def commitProjectFiles():
  path = realpath(app.config, request.form['project'])
  if path:
    return gitCommit(path, request.form['msg'])
  else:
    return jsonify(code=0, result="Can not read folder: Permission Denied")


def pushProjectFiles():
  path = realpath(app.config, request.form['project'])
  if path:
    return gitPush(path)
  else:
    return jsonify(code=0, result="Can not read folder: Permission Denied")


def pullProjectFiles():
  path = realpath(app.config, request.form['project'])
  if path:
    return gitPull(path)
  else:
    return jsonify(code=0, result="Can not read folder: Permission Denied")


def checkFileType():
  path = realpath(app.config, request.form['path'])
  if not path:
    return jsonify(code=0, result="Can not open file: Permission Denied!")
  if isText(path):
    return jsonify(code=1, result="text")
  else:
    return jsonify(code=0,
                   result="Can not open a binary file, please select a text file!")


def getmd5sum():
  realfile = realpath(app.config, request.form['file'])
  if not realfile:
    return jsonify(code=0, result="Can not open file: Permission Denied!")
  md5 = md5sum(realfile)
  if md5:
    return jsonify(code=1, result=md5)
  else:
    return jsonify(code=0, result="Can not get md5sum for this file!")


#return information about state of slapgrid process
def slapgridResult():
  software_state = isSoftwareRunning(app.config)
  instance_state = isInstanceRunning(app.config)
  log_result = {
    'content': '',
    'position': 0,
    'truncated': False
  }
  if request.form['log'] in ['software', 'instance']:
    log_file = request.form['log'] + "_log"
    if os.path.exists(app.config[log_file]):
      log_result = readFileFrom(open(app.config[log_file]),
                                int(request.form['position']))
  build_result = getSlapgridResult(app.config, 'software')
  run_result = getSlapgridResult(app.config, 'instance')
  software_info = {'state':software_state,
                   'last_build':build_result['last_build'],
                   'success':build_result['success']}
  instance_info = {'state':instance_state,
                   'last_build':run_result['last_build'],
                   'success':run_result['success']}
  return jsonify(software=software_info, instance=instance_info,
                 result=(instance_state or software_state), content=log_result)


def stopSlapgrid():
  counter_file = os.path.join(app.config['runner_workdir'], '.turn-left')
  open(counter_file, 'w+').write(str(0))
  result = sup_process.killRunningProcess(app.config, request.form['type'])
  return jsonify(result=result)


def getPath():
  files = request.form['file'].split('#')
  list = []
  for p in files:
    path = realpath(app.config, p)
    if not path:
      list = []
      break
    else:
      list.append(path)
  realfile = '#'.join(list)
  if not realfile:
    return jsonify(code=0,
                   result="Can not access to this file: Permission Denied!")
  else:
    return jsonify(code=1, result=realfile)


def saveParameterXml():
  """
  Update instance parameter into a local xml file.
  """
  project = os.path.join(app.config['etc_dir'], ".project")
  if not os.path.exists(project):
    return jsonify(code=0, result="Please first open a Software Release")
  content = request.form['parameter'].encode("utf-8")
  param_path = os.path.join(app.config['etc_dir'], ".parameter.xml")
  try:
    with open(param_path, 'w') as f:
      f.write(content)
    result = readParameters(param_path)
  except Exception as e:
    result = str(e)
  software_type = None
  if request.form['software_type']:
    software_type = request.form['software_type']
  if type(result) == type(''):
    return jsonify(code=0, result=result)
  else:
    try:
      updateInstanceParameter(app.config, software_type)
    except Exception as e:
      return jsonify(
        code=0,
        result="An error occurred while applying your settings!<br/>%s" % e)
    return jsonify(code=1, result="")


def getSoftwareType():
  software_type_path = os.path.join(app.config['etc_dir'], ".software_type.xml")
  if os.path.exists(software_type_path):
    return jsonify(code=1, result=open(software_type_path).read())
  return jsonify(code=1, result="default")


#read instance parameters into the local xml file and return a dict
def getParameterXml(request):
  param_path = os.path.join(app.config['etc_dir'], ".parameter.xml")
  if not os.path.exists(param_path):
    default = '<?xml version="1.0" encoding="utf-8"?>\n<instance>\n</instance>'
    return jsonify(code=1, result=default)
  if request == "xml":
    parameters = open(param_path).read()
  else:
    parameters = readParameters(param_path)
  if type(parameters) == type('') and request != "xml":
    return jsonify(code=0, result=parameters)
  else:
    return jsonify(code=1, result=parameters)


#update user-defined slapgrid parameters
def updateBuildAndRunConfig():
  code = 1
  try:
    max_run_instance = int(request.form['max_run_instance'].strip())
    max_run_software = int(request.form['max_run_software'].strip())
  except ValueError:
    code = 0
    result = "Error! You should have provided an integer"
  run_instance = (True if request.form['run_instance']=="true" else False)
  run_software = (True if request.form['run_software']=="true" else False)
  if code:
    params =  {}
    params['run_instance'] = run_instance
    params['run_software'] = run_software
    params['max_run_instance'] = max_run_instance
    params['max_run_software'] = max_run_software
    saveBuildAndRunParams(app.config, params)
    result = "Your parameters have correctly been updated"
  return jsonify(code=code, result=result)


#update user account data
def updateAccount():

  username = request.form['username'].strip()
  password = request.form['password'].strip()
  new_password = request.form['new_password'].strip()
  email = request.form['email'].strip()
  name = request.form['name'].strip()

  if username and password and new_password:
    if not checkUserCredential(app.config, username, password):
      return jsonify(code=0, result="Username and password doesn't match for '%s'" % username)

    result = updateUserCredential(app.config, username, new_password)
    if not result:
      return jsonify(code=0, result="Failed to update Credentials!")

  try:
    updateGitConfig(app.config['default_repository_path'], name, email)
  except GitCommandError, e:
    return jsonify(code=0, result=str(e))
  git_user_file = os.path.join(app.config['etc_dir'], '.git_user')
  with codecs.open(git_user_file, 'w', encoding='utf-8') as gfile:
    gfile.write(u'{};{}'.format(name, email))
  return jsonify(code=1, result="")


#update user account data
@app.route("/configAccount", methods=['POST'])
def configAccount():
  """last_account = getSession(app.config)
  if last_account:
    return jsonify(code=0,
                   result="Unable to respond to your request, permission denied.")

  account = []
  account.append(request.form['username'].strip())
  account.append(request.form['password'].strip())
  account.append(request.form['email'].strip())
  account.append(request.form['name'].strip())
  code = request.form['rcode'].strip()
  recovery_code = getRcode(app.config)
  if code != recovery_code:
    return jsonify(code=0, result="Your password recovery code is not valid!")
  result = saveSession(app.config, account)
  if type(result) == type(""):
    return jsonify(code=0, result=result)
  else:
    return jsonify(code=1, result="")"""

def addUser():
  if createNewUser(app.config, request.form['username'],
                   request.form['password']):
    return jsonify(code=1, result="New user succesfully saved")
  else:
    return jsonify(code=0, result="Problem while creating new user")


#Global File Manager
def fileBrowser():
  if request.method == 'POST':
    filename = request.form.get('filename', '').encode('utf-8')
    dir = request.form['dir'].encode('utf-8')
    newfilename = request.form.get('newfilename', '').encode('utf-8')
    files = request.form.get('files', '').encode('utf-8')
    if not request.form.has_key('opt') or not request.form['opt']:
      opt = 1
    else:
      opt = int(request.form['opt'])
  else:
    opt = int(request.args.get('opt'))

  try:
    if opt == 1:
      #list files and directories
      result = file_request.listDirs(dir)
    elif opt == 2:
      #Create file
      result = file_request.makeFile(dir, filename)
    elif opt == 3:
      #Create directory
      result = file_request.makeDirectory(dir, filename)
    elif opt == 4:
      #Delete a list of files or/and directories
      result = file_request.deleteItem(dir, files)
    elif opt == 5:
      #copy a lis of files or/and directories
      result = file_request.copyItem(dir, files)
    elif opt == 6:
      #rename file or directory
      result = file_request.rename(dir, filename, newfilename)
    elif opt == 7:
      result = file_request.copyItem(dir, files, del_source=True)
    elif opt == 8:
      #donwload file
      filename = request.args.get('filename').encode('utf-8')
      result = file_request.downloadFile(request.args.get('dir').encode('utf-8'),
                filename)
      try:
        return send_file(result, attachment_filename=filename, as_attachment=True)
      except:
        abort(404)
    elif opt == 9:
      result = file_request.readFile(dir, filename, False)
    elif opt == 11:
      #Upload file
      result = file_request.uploadFile(dir, request.files)
    elif opt == 14:
      #Copy file or directory as ...
      result = file_request.copyAsFile(dir, filename, newfilename)
    elif opt == 16:
      #zip file
      result = file_request.zipFile(dir, filename, newfilename)
    elif opt == 17:
      #zip file
      result = file_request.unzipFile(dir, filename, newfilename)
    elif opt == 20:
      #Fancy Load folder
      key = request.args.get('key')
      dir = request.args.get('dir').encode('utf-8')
      listfiles = request.args.get('listfiles', '')
      data = file_request.fancylistDirs(dir, key, listfiles)
      result = json.dumps(data)
    else:
      result = "ARGS PARSE ERROR: Bad option..."
  except Exception as e:
    return str(e)
  return result


def editFile():
  return render_template('editFile.html', workDir='workspace',
    profile=urllib.unquote(request.args.get('profile', '')),
    projectList=listFolder(app.config, 'workspace'),
    filename=urllib.unquote(request.args.get('filename', '')))

def shell():
  return render_template('shell.html')


def isSRReady():
  return isSoftwareReleaseReady(app.config)


def runCommand():
  cwd = open(app.config['minishell_cwd_file'], 'r').read().strip()
  command = request.form.get("command", '').strip()
  parsed_commands = command.split(';');
  # does the user want to change current directory ?
  for cmd in parsed_commands:
    if 'cd' == cmd[:2]:
      cmd = cmd.split(' ');
      real_cmd = cmd[:]
      if len(cmd) == 1:
        cmd.append(os.environ.get('HOME'))
      # shorten directory's name, to avoid things like : /a/../b
      cd_dir = os.path.realpath(os.path.join(cwd, cmd[1]))
      if os.path.exists(cd_dir) and os.path.isdir(cd_dir):
        cwd = cd_dir
        # save new cwd in the config file
        open(app.config['minishell_cwd_file'], 'w').write(cwd)
        # if the command was just cd, execute it. Otherwise, execute the rest
        command = command.replace(' '.join(real_cmd), '').strip(';')
        if not command:
          return jsonify(path=cwd, data="Changed directory, now in : "+cwd)
  try:
    setMiniShellHistory(app.config, command)
    command = "timeout 600 " + command
    return jsonify(path=cwd, data=subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True, cwd=cwd, env={'PATH': app.config['path']}))
  except subprocess.CalledProcessError as e:
    return jsonify(path=cwd, data=e.output, returncode=e.returncode, error=True)


def getMiniShellHistory():
  history_file = app.config['minishell_history_file']
  if not os.path.exists(history_file):
    return ""
  history = open(history_file, 'r').readlines()
  for line, text in enumerate(history):
    history[line] = text.strip()
  return json.dumps(history)


#Setup List of URLs
app.add_url_rule('/', 'home', home)
app.add_url_rule('/browseWorkspace', 'browseWorkspace', browseWorkspace)
app.add_url_rule('/editSoftwareProfile', 'editSoftwareProfile',
                editSoftwareProfile)
app.add_url_rule('/inspectSoftware', 'inspectSoftware', inspectSoftware)
app.add_url_rule('/removeSoftware', 'removeSoftware', removeSoftware)
app.add_url_rule('/runSoftwareProfile', 'runSoftwareProfile',
                 runSoftwareProfile, methods=['GET', 'POST'])
app.add_url_rule('/editInstanceProfile', 'editInstanceProfile',
                 editInstanceProfile)
app.add_url_rule('/inspectInstance', 'inspectInstance',
                 inspectInstance, methods=['GET'])
app.add_url_rule('/supervisordStatus', 'supervisordStatus',
                 supervisordStatus, methods=['GET'])
app.add_url_rule('/runInstanceProfile', 'runInstanceProfile',
                 runInstanceProfile, methods=['GET', 'POST'])
app.add_url_rule('/removeInstance', 'removeInstance', removeInstance)
app.add_url_rule('/viewLog', 'viewLog',
                 viewLog, methods=['GET'])
app.add_url_rule("/getFileLog", 'getFileLog', getFileLog,
                 methods=['POST'])
app.add_url_rule('/stopAllPartition', 'stopAllPartition',
                 stopAllPartition, methods=['GET'])
app.add_url_rule('/startAllPartition', 'startAllPartition',
                 startAllPartition, methods=['GET'])
app.add_url_rule('/tailProcess/name/<process>', 'tailProcess',
                 tailProcess, methods=['GET'])
app.add_url_rule('/startStopProccess/name/<process>/cmd/<action>',
                 'startStopProccess', startStopProccess, methods=['GET'])
app.add_url_rule("/getParameterXml/<request>", 'getParameterXml',
                 getParameterXml, methods=['GET'])
app.add_url_rule('/getSoftwareType', 'getSoftwareType',
                 getSoftwareType, methods=['GET'])
app.add_url_rule("/stopSlapgrid", 'stopSlapgrid', stopSlapgrid, methods=['POST'])
app.add_url_rule("/slapgridResult", 'slapgridResult',
                 slapgridResult, methods=['POST'])
app.add_url_rule("/getmd5sum", 'getmd5sum', getmd5sum, methods=['POST'])
app.add_url_rule("/checkFileType", 'checkFileType', checkFileType,
                 methods=['POST'])
app.add_url_rule("/commitProjectFiles", 'commitProjectFiles', commitProjectFiles,
                 methods=['POST'])
app.add_url_rule("/pullProjectFiles", 'pullProjectFiles', pullProjectFiles,
                 methods=['POST'])
app.add_url_rule("/pushProjectFiles", 'pushProjectFiles', pushProjectFiles,
                 methods=['POST'])
app.add_url_rule("/getProjectDiff", 'getProjectDiff', getProjectDiff,
                 methods=['POST'])
app.add_url_rule("/newBranch", 'newBranch', newBranch, methods=['POST'])
app.add_url_rule("/changeBranch", 'changeBranch', changeBranch, methods=['POST'])
app.add_url_rule("/saveFileContent", 'saveFileContent', saveFileContent,
                 methods=['POST'])
app.add_url_rule("/removeSoftwareDir", 'removeSoftwareDir', removeSoftwareDir,
                 methods=['POST'])
app.add_url_rule("/getFileContent", 'getFileContent', getFileContent,
                 methods=['POST'])
app.add_url_rule("/removeFile", 'removeFile', removeFile, methods=['POST'])
app.add_url_rule("/createFile", 'createFile', createFile, methods=['POST'])
app.add_url_rule("/editCurrentProject", 'editCurrentProject', editCurrentProject)
app.add_url_rule("/getProjectStatus", 'getProjectStatus', getProjectStatus,
                 methods=['POST'])
app.add_url_rule('/openProject/<method>', 'openProject', openProject,
                 methods=['GET'])
app.add_url_rule("/setCurrentProject", 'setCurrentProject', setCurrentProject,
                 methods=['POST'])
app.add_url_rule("/checkFolder", 'checkFolder', checkFolder, methods=['POST'])
app.add_url_rule('/createSoftware', 'createSoftware', createSoftware,
                 methods=['POST'])
app.add_url_rule('/cloneRepository', 'cloneRepository', cloneRepository,
                 methods=['POST'])
app.add_url_rule('/listDirectory', 'listDirectory', listDirectory, methods=['POST'])
app.add_url_rule('/manageRepository', 'manageRepository', manageRepository)
app.add_url_rule("/saveParameterXml", 'saveParameterXml', saveParameterXml,
                 methods=['POST'])
app.add_url_rule("/getPath", 'getPath', getPath, methods=['POST'])
app.add_url_rule("/myAccount", 'myAccount', myAccount)
app.add_url_rule("/updateAccount", 'updateAccount', updateAccount,
                 methods=['POST'])
app.add_url_rule("/updateBuildAndRunConfig", 'updateBuildAndRunConfig', updateBuildAndRunConfig,
                 methods=['POST'])
app.add_url_rule("/fileBrowser", 'fileBrowser', fileBrowser,
                 methods=['GET', 'POST'])
app.add_url_rule("/editFile", 'editFile', editFile, methods=['GET'])
app.add_url_rule('/shell', 'shell', shell)
app.add_url_rule('/isSRReady', 'isSRReady', isSRReady)
app.add_url_rule('/addUser', 'addUser', addUser, methods=['POST'])
app.add_url_rule('/getSlapgridParameters', 'getSlapgridParameters', getSlapgridParameters, methods=['GET'])
app.add_url_rule('/runCommand', 'runCommand', runCommand, methods=['POST'])
app.add_url_rule("/getMiniShellHistory", 'getMiniShellHistory', getMiniShellHistory, methods=['GET'])
