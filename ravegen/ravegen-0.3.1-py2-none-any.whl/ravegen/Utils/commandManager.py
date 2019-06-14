import Utils.sad as sad
import utils
import subprocess

def _executeCommand(command, fistrArg, args, writeFile = None):
    runCommand = command.split(" ") + [fistrArg] + list(args)
    runCommand.remove('')
    runCommand = [i.strip(' ') for i in runCommand]
    if writeFile is None:
        subprocess.call(runCommand, shell=False)
    else:
        writeFileObj = open(writeFile, "w+")
        subprocess.call(runCommand, shell=False, stdout=writeFileObj, stderr=writeFileObj)
        writeFileObj.close()



def runPackageManagerInstall(package, *args):
    dist = utils.getDist()
    if dist == sad._FEDORA_DIST_NAME_:
        _executeCommand(sad._LINUX_SUDO_COMMAND_, sad._FEDORA_PACKAGE_MANADER_COMMAND_, [sad._LINUX_PACKAGE_MANAGER_INSTALL_OPTION, package] + list(args))
    if dist == sad._UBUNTU_DIST_NAME_:
        _executeCommand(sad._LINUX_SUDO_COMMAND_, sad._UBUNTU_PACKAGE_MANAGER_COMMAND_, [sad._LINUX_PACKAGE_MANAGER_INSTALL_OPTION, package] + list(args))

def runMkdirCommand(directory, *args):
    _executeCommand(sad._LINUX_MKDIR_COMMAND_, directory, args)

def runRmCommand(firstFile, *args):
    _executeCommand(sad._LINUX_RM_COMMAND_, firstFile, args)

def runRmDirCommand(directory, *args):
    _executeCommand(sad._LINUX_RM_COMMAND_DIR, directory, args)

def runLsCommand(directory, writeFile = None):
    _executeCommand(sad._LINUX_LS_COMMAND_, directory, [], writeFile=writeFile)

def runCpCommand(firstFile, dest, *args):
    _executeCommand(sad._LINUX_CP_COMMAND_, firstFile, list(args) + [dest])

def runCpDirCommand(firstDirectory, dest, *args):
    _executeCommand(sad._LINUX_CP_DIR_COMMAND_, firstDirectory, list(args) + [dest])

def runEchoCommand(text, dest):
    _executeCommand(sad._LINUX_ECHO_COMMAND_, "'" + text + "'", [], writeFile=dest)

def runTouchCommand(firstFile, *args):
    _executeCommand(sad._LINUX_TOUCH_COMMAND_, firstFile, args)

def runTouchSudoCommand(firstFile, *args):
    _executeCommand(sad._LINUX_SUDO_COMMAND_, sad._LINUX_TOUCH_COMMAND_, [firstFile] + list(args))

def runGitInitCommand():
    _executeCommand(sad._LINUX_GIT_COMAND_, sad._LINUX_GIT_INIT_COMMAND_, [])

def runGitAddRemoteCommand(branch, url):
    _executeCommand(sad._LINUX_GIT_COMAND_, sad._LINUX_GIT_REMOTE_OPTION_ , [sad._LINUX_GIT_ADD_OPTION_, branch, url])

def runGitSetRemoteUrlCommand(branch, url):
    _executeCommand(sad._LINUX_GIT_COMAND_, sad._LINUX_GIT_REMOTE_OPTION_, [sad._LINUX_GIT_REMOTE_SET_URL_OPTION, branch, url])

def runGitRemoteCommand(writeFile = None):
    _executeCommand(sad._LINUX_GIT_COMAND_, sad._LINUX_GIT_REMOTE_OPTION_, [sad._LINUX_GIT_REMOTE_VERBOSE_OPTION], writeFile=writeFile)

def runGitAdd(directory_file, *args):
    _executeCommand(sad._LINUX_GIT_COMAND_, sad._LINUX_GIT_ADD_OPTION_, [directory_file] + args)

def runGitAddAll():
    _executeCommand(sad._LINUX_GIT_COMAND_, sad._LINUX_GIT_ADD_OPTION_, [sad._LINUX_ALL_TAG_])

def runGitCommitCommand(message):
    commitOption = sad._LINUX_GIT_COMMIT_OPTION_.split(" ")
    _executeCommand(sad._LINUX_GIT_COMAND_, commitOption[0], commitOption[1:] + [message])

def runGitPushCommand(branchSource, branchDest):
    _executeCommand(sad._LINUX_GIT_COMAND_, sad._LINUX_GIT_PUSH_OPTION_, [branchSource, branchDest])

def runPythonCommand(pythonFile, *args):
    _executeCommand(sad._LINUX_PYTHON_COMMAND_, pythonFile, args)

def runPythonSiteCommand(writeFile):
    _executeCommand(sad._LINUX_PYTHON_COMMAND_, sad._LINUX_PYTHON_M_OPTION_, [sad._LINUX_PYTHON_SITE_OPTION_, sad._LINUX_PYTHON_USER_SITE_OPTION_], writeFile=writeFile)

def runPipShowRavegen(writeFile):
    _executeCommand(sad._LINUX_PIP_COMMAND_, sad._LINUX_PIP_SHOW_OPTION_, [sad._RAVEGEN_SRC_PATH_], writeFile=writeFile)

def runPipInstallReq():
    _executeCommand(sad._LINUX_SUDO_COMMAND_, sad._LINUX_PIP_COMMAND_, [sad._LINUX_PIP_INSTALL_OPTION_, sad._LINUX_PIP_TAGET_OPTION_, sad._GAE_LIB_DIR_NAME_, sad._LINUX_PIP_REQ_OPTION_, sad._GAE_REQ_FILE_NAME])

def runHerokuCreateCommand(projectName):
    _executeCommand(sad._LINUX_HEROKU_COMMAND_, sad._LINUX_HEROKU_CREATE_OPTION_, [projectName])

def runHerokuInfoCommand(projectName, writeFile = None):
    _executeCommand(sad._LINUX_HEROKU_COMMAND_, sad._LINUX_HEORKU_INFO_OPTION_, [projectName], writeFile=writeFile)

def runHerokuDestroyCommand(projectName):
    _executeCommand(sad._LINUX_HEROKU_COMMAND_, sad._LINUX_HEROKU_DESTORY_OPTION_, [projectName, sad._LINUX_HEROKU_DESTROY_CONFIRM_, projectName])

def runHerokuToken(writeFile = None):
    _executeCommand(sad._LINUX_HEROKU_COMMAND_, sad._LINUX_HEROKU_TOKEN_OPTION_, [], writeFile=writeFile)

def runHerokuLogin():
    _executeCommand(sad._LINUX_HEROKU_COMMAND_, sad._LINUX_HEROKU_LOGIN_OPTION_, [])

def runSnapListCommand(writeFile = None):
    _executeCommand(sad._LINUX_SNAP_COMMAND_, sad._LINUX_SNAP_LIST_OPTION_, [], writeFile=writeFile)

def runSnapInstallCommand(package, version):
    _executeCommand(sad._LINUX_SUDO_COMMAND_, sad._LINUX_SNAP_COMMAND_,  [sad._LINUX_SNAP_INSTALL_OPTION_, package, version])

def runGAEAuthListCommand(writeFile):
    _executeCommand(sad._LINUX_GAE_COMMAND, sad._LINUX_GAE_AUTH_OPTION, [sad._LINUX_GAE_AUTH_LIST_OPTION], writeFile=writeFile)

def runGAELogin():
    _executeCommand(sad._LINUX_GAE_COMMAND, sad._LINUX_GAE_AUTH_OPTION, [sad._LINUX_GAE_AUTH_LOGIN_OPTION])

def runGAENewProject(projectName):
    _executeCommand(sad._LINUX_GAE_COMMAND, sad._LINUX_GAE_PROJECTS_OPTION, [sad._LINUX_GAE_PROJECTS_CREATE_OPTION, projectName])

def runGAEListProjects(writeFile):
    _executeCommand(sad._LINUX_GAE_COMMAND, sad._LINUX_GAE_PROJECTS_OPTION, [sad._LINUX_GAE_PROJECTS_LIST_OPTION], writeFile=writeFile)

def runGAEDeleteProject(projectName):
    _executeCommand(sad._LINUX_GAE_COMMAND, sad._LINUX_GAE_PROJECTS_OPTION, [sad._LINUX_GAE_PROJECTS_DELETE_OPTION, projectName])

def runGAESetProject(projectName):
    _executeCommand(sad._LINUX_GAE_COMMAND, sad._LINUX_GAE_CONFIG_OPTION, [sad._LINUX_GAE_CONFIG_SET_OPTION, sad._LINUX_GAE_CONFIG_PROJECT_OPTION, projectName])

def runGAEDeploy():
    _executeCommand(sad._LINUX_GAE_COMMAND, sad._LINUX_GAE_APP_OPTION, [sad._LINUX_GAE_APP_DEPLOY_OPTION])

def runCurlCommand(url):
    _executeCommand(sad._LINUX_CURL_COMMAND, url, [])
