import time
import sys
import Utils.sad as sad
import Utils.inputManager as inputManager
import Utils.commandManager as commandManager
import Utils.logManager as logManager
import Utils.utils as utils
import Utils.errorHandler as errorHandler
import RaveEngine.configManager as configManager

herokuErrorHandler = errorHandler.ErrorHandler("Heroku Manager")

def initConfiguration():
    logManager.printVerbose("Verifying configuration...")
    logManager.printVerbose("Verifying Heroku installation...")
    _verifyHerokuInstallation()
    logManager.printVerbose("Verifying Heroku login...")
    while True:
        if not _verifyHerokuLogIn():
            logManager.printVerbose("Can't find heroku token")
            logManager.printVerbose("Heorku login...")
            _herokuLogIn()
        else:
            break
    config = configManager.getConfig()
    projectNameFlag = True
    initProjectFlag = True
    gitInitFlag = True
    gitHerokuFlag = True
    projectName = configManager.get(config, sad._DEPLOY_HEROKU_OPTION, sad._CONFIG_PROJECT_NAME_OPTION_)
    logManager.printVerbose("Verifiying project name...")
    if projectName != None and projectName != sad._INIT_CONFIG_PROJECT_NAME:
        logManager.printVerbose("Project name found: " + projectName)
        projectNameFlag = False
    logManager.printVerbose("Verifiying project in heroku...")
    if _verifyProject(projectName):
        logManager.printVerbose("The project has already been created in heroku")
        initProjectFlag = False
    if utils.file_Or_Directory_Exists(sad._ACTUAL_PATH, sad._GIT_DIR_):
        logManager.printVerbose("Git has already been created")
        gitInitFlag = False
    gitHerokuFlag =  _verifyRemoteHeroku(configManager.get(config, sad._DEPLOY_HEROKU_OPTION, sad._CONFIG_GIT_OPTION_))
    if gitHerokuFlag > 0:
        logManager.printVerbose("Git has already been configured")


    _initConfiguration(projectNameFlag, initProjectFlag, gitInitFlag, gitHerokuFlag)
    logManager.printVerbose("All Configurations... OK")

def deploy():
    _crateSkeleton()
    commandManager.runGitAddAll()
    logManager.printVerbose("Commiting changes...")
    commandManager.runGitCommitCommand(utils.getTime() + ": Deploy bot in heroku")
    logManager.printVerbose("Deploying bot in Heroku...")
    commandManager.runGitPushCommand(sad._DEPLOY_HEROKU_OPTION, sad._GIT_MASTER)
    _deleteSkeleton()
    logManager.printVerbose("Deploying bot in Heroku...OK")


def deleteCloudApp():
    config = configManager.getConfig()
    projectName = configManager.get(config, sad._DEPLOY_HEROKU_OPTION, sad._CONFIG_PROJECT_NAME_OPTION_)
    if projectName != None and projectName != sad._INIT_CONFIG_PROJECT_NAME:
        commandManager.runHerokuDestroyCommand(projectName)
        configManager.set(config, sad._DEPLOY_HEROKU_OPTION, sad._CONFIG_PROJECT_NAME_OPTION_, "")
        configManager.set(config, sad._CONFIG_RAVEGEN_SECTION_, sad._CONFIG_DEPLOY_URL_OPTION, "")
        configManager.set(config, sad._CONFIG_RAVEGEN_SECTION_, sad._CONFIG_WEBHOOK_PATH_OPTION, "")
        configManager.set(config, sad._DEPLOY_HEROKU_OPTION, sad._CONFIG_GIT_OPTION_, "")

def sigintHandler(sig, frame):
    _deleteSkeleton()
    print "AAAAAAAAAAAAAA"
    sys.exit()

def _initConfiguration(projectNameFlag = True, initProjectFlag = True, gitInitFlag = True, gitHerokuFlag = -1):
    config = configManager.getConfig()
    if gitInitFlag:
        logManager.printVerbose("Creating git...")
        commandManager.runGitInitCommand()
        gitHerokuFlag = -1
    if projectNameFlag:
        logManager.printVerbose("Project name doesn't found")
        _getNewHerokuName(config)
        initProjectFlag = True
    if initProjectFlag:
        logManager.printVerbose("Project hasn't been created in heroku")
        erroFlag = False
        while True:
            if erroFlag:
                logManager.printVerbose("The project can't created in heroku. Read the errors above and chose a new heroku project name")
                _getNewHerokuName(config)
            projectName = configManager.get(config, sad._DEPLOY_HEROKU_OPTION, sad._CONFIG_PROJECT_NAME_OPTION_)
            token = configManager.get(config, sad._CONFIG_RAVEGEN_SECTION_, sad._CONFIG_TOKEN_OPTION_)
            deployUrl = sad._HTTPS_ + projectName + sad._HEROKU_URL
            gitUrl = sad._HTTPS_ + sad._HEORKU_GIT_URL + projectName + sad._GIT_EXTENTION
            commandManager.runHerokuCreateCommand(projectName)
            if _verifyProject(projectName):
                configManager.set(config, sad._CONFIG_RAVEGEN_SECTION_, sad._CONFIG_DEPLOY_URL_OPTION, deployUrl)
                configManager.set(config, sad._CONFIG_RAVEGEN_SECTION_, sad._CONFIG_WEBHOOK_PATH_OPTION, token)
                configManager.set(config, sad._DEPLOY_HEROKU_OPTION, sad._CONFIG_GIT_OPTION_, gitUrl)
                gitHerokuFlag =  _verifyRemoteHeroku(gitUrl)
                break
            else:
                erroFlag = True
    if gitHerokuFlag == -1:
        logManager.printVerbose("Adding git remote heroku...")
        gitUrl = configManager.get(config, sad._DEPLOY_HEROKU_OPTION, sad._CONFIG_GIT_OPTION_)
        commandManager.runGitAddRemoteCommand(sad._DEPLOY_HEROKU_OPTION, gitUrl)
    if gitHerokuFlag == 0:
        logManager.printVerbose("Setting git remote heroku...")
        gitUrl = configManager.get(config, sad._DEPLOY_HEROKU_OPTION, sad._CONFIG_GIT_OPTION_)
        commandManager.runGitSetRemoteUrlCommand(sad._DEPLOY_HEROKU_OPTION, gitUrl)




def _crateSkeleton():
    procFile = open(sad._HEROKU_PROCFILE_NAME, 'w')
    procFile.write("web: " + sad._LINUX_PYTHON_COMMAND_ + sad.OUTPUT_BOT_PATH)
    procFile.close()
    commandManager.runCpCommand(sad._CONFIG_REQ_FILE_PAHT_, sad._HEROKU_REQ_FILE_NAME)
    commandManager.runCpCommand(sad._CONFIG_RUNTIME_FILE_PATH_, sad._HEROKU_RUNTIME_FILE_NAME)

def _deleteSkeleton():
    commandManager.runRmCommand(sad._HEROKU_PROCFILE_NAME, sad._HEROKU_REQ_FILE_NAME, sad._HEROKU_RUNTIME_FILE_NAME)

def _verifyProject(projectName):
    if projectName is None:
        projectName = "None"
    commandManager.runHerokuInfoCommand(projectName, sad._TEMP_HEROKU_INFO_FILE_NAME)
    tempFile = open(sad._TEMP_HEROKU_INFO_FILE_NAME, 'r')
    line = tempFile.readline()
    tokens = line.split(' ')
    tempFile.close()
    commandManager.runRmCommand(sad._TEMP_HEROKU_INFO_FILE_NAME)
    if(tokens[0] == '==='):
        return True
    return False

def _verifyRemoteHeroku(gitUrl):
    if gitUrl is None:
        return -1
    commandManager.runGitRemoteCommand(sad._TEMP_GIT_REMOTE_FILE_NAME)
    tempFile = open(sad._TEMP_GIT_REMOTE_FILE_NAME, 'r')
    for line in tempFile:
        tokens = line.split('\t')
        tokens[1] = tokens[1].split(' ')[0]
        if(tokens[0] == sad._DEPLOY_HEROKU_OPTION):
            tempFile.close()
            commandManager.runRmCommand(sad._TEMP_GIT_REMOTE_FILE_NAME)
            if(tokens[1] == gitUrl):
                return 1
            return 0
    tempFile.close()
    commandManager.runRmCommand(sad._TEMP_GIT_REMOTE_FILE_NAME)
    return -1

def _verifyHerokuInstallation():
    commandManager.runLsCommand(sad._HEROKU_SNAP_PATH, writeFile=sad._TEMP_LS_VERIFY_FILE_NAME)
    tempFile = open(sad._TEMP_LS_VERIFY_FILE_NAME, 'r')
    line = tempFile.readline()
    tempFile.close()
    commandManager.runRmCommand(sad._TEMP_LS_VERIFY_FILE_NAME)
    tokens = line.split(' ')
    tokens[0] = tokens[0].rstrip('\n')
    if(tokens[0] != sad._HEROKU_SNAP_PATH):
        logManager.printVerbose("Snap is not installed")
        if(utils.hasSupport()):
            answer = inputManager.getYesNoAnswer("Do you want to install snapd? (y/n):")
            if answer:
                commandManager.runPackageManagerInstall(sad._HEORKU_SNAP_PACKAGE)
                logManager.printVerbose("Waiting for snapd...")
                time.sleep(30)
            else:
                herokuErrorHandler.addError("Snap is not installed", sad._CRITICAL_ERROR_)
        else:
            herokuErrorHandler.addError("Snap is not installed", sad._CRITICAL_ERROR_)

    herokuErrorHandler.handle()

    commandManager.runSnapListCommand(sad._TEMP_SNAP_LIST_FILE_NAME)
    tempFile = open(sad._TEMP_SNAP_LIST_FILE_NAME, 'r')
    flag = False
    for line in tempFile:
        tokens = line.split(' ')
        if(tokens[0] == sad._DEPLOY_HEROKU_OPTION):
            flag = True
            break
    tempFile.close()
    commandManager.runRmCommand(sad._TEMP_SNAP_LIST_FILE_NAME)
    if not flag:
        logManager.printVerbose("heroku-cli is not installed")
        answer = inputManager.getYesNoAnswer("Do you want to install heroku-cli? (y/n):")
        if answer:
            commandManager.runSnapInstallCommand(sad._DEPLOY_HEROKU_OPTION, sad._HEROKU_HEROKU_CLI_VERSION_)
        else:
            herokuErrorHandler.addError("heroku-cli is not installerd", sad._CRITICAL_ERROR_)

    herokuErrorHandler.handle()

def _verifyHerokuLogIn():
    commandManager.runHerokuToken(sad._TEMP_HEROKU_TOKEN_FILE_NAME)
    tempFile = open(sad._TEMP_HEROKU_TOKEN_FILE_NAME)
    count = 0
    for _ in tempFile:
        count += 1
    tempFile.close()
    commandManager.runRmCommand(sad._TEMP_HEROKU_TOKEN_FILE_NAME)
    if count > 1:
        return True
    return False

def _herokuLogIn():
    commandManager.runHerokuLogin()

def _getNewHerokuName(config):
    projectName = inputManager.getInput("Enter new Heroku Project Name: ")
    configManager.set(config, sad._DEPLOY_HEROKU_OPTION, sad._CONFIG_PROJECT_NAME_OPTION_, projectName)
